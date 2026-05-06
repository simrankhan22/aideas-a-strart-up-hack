import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

from config_app import load_config


ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
REQUIRED_RESPONSE_KEYS = ["call_speeches"]


def extract_json(text: str, required_keys: list[str] | None = None) -> dict:
    raw = text.strip()
    if not raw:
        raise ValueError("Model returned an empty response.")

    candidates = [raw]
    fenced = re.findall(r"```(?:json)?\s*([\s\S]*?)```", raw, flags=re.IGNORECASE)
    candidates.extend(block.strip() for block in fenced if block.strip())

    decoder = json.JSONDecoder()
    for idx, ch in enumerate(raw):
        if ch != "{":
            continue
        try:
            parsed, end = decoder.raw_decode(raw[idx:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            candidates.append(raw[idx : idx + end])

    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidates.append(raw[start : end + 1])

    seen = set()
    unique = []
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        unique.append(candidate)

    unique.sort(key=len, reverse=True)
    for candidate in unique:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            if required_keys and not all(key in parsed for key in required_keys):
                continue
            return parsed

    raise ValueError("Could not parse valid JSON from model response.")


def load_call_targets(path: Path) -> tuple[str, str, list[dict]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    targets = payload.get("call_targets", [])
    if not isinstance(targets, list):
        targets = []

    valid_targets = []
    for target in targets:
        if not isinstance(target, dict):
            continue

        phone = target.get("contact_number_with_country_code")
        if phone is None:
            continue
        if isinstance(phone, str) and not phone.strip():
            continue
        if isinstance(phone, str) and phone.strip().lower() in {"null", "none"}:
            continue

        org_name = str(target.get("org_name") or "").strip()
        if not org_name:
            continue

        ask_list = target.get("ask_and_clarify", [])
        if isinstance(ask_list, str):
            ask_list = [ask_list.strip()] if ask_list.strip() else []
        elif isinstance(ask_list, list):
            ask_list = [str(x).strip() for x in ask_list if str(x).strip()]
        else:
            ask_list = []

        valid_targets.append(
            {
                "org_name": org_name,
                "contact_number_with_country_code": str(phone).strip(),
                "country_code": (
                    str(target.get("country_code")).strip()
                    if target.get("country_code")
                    else None
                ),
                "ask_and_clarify": ask_list,
                "source_urls": target.get("source_urls", []),
            }
        )

    return (
        str(payload.get("client_name") or "").strip(),
        str(payload.get("target_country") or "").strip(),
        valid_targets,
    )


def fallback_script(client_name: str, target: dict) -> dict:
    org_name = target["org_name"]
    questions = target.get("ask_and_clarify", [])
    if not questions:
        questions = ["Confirm the latest official requirement and where it is documented."]

    question_lines = "\n".join(f"- {q}" for q in questions[:5])
    speech = (
        f"Hello, this is a compliance verification call on behalf of {client_name or 'our company'}. "
        f"I'm calling regarding {org_name}. "
        "Could you help clarify a few points so we can follow the correct official process?\n"
        f"{question_lines}\n"
        "If possible, please point us to the official page or reference for each answer."
    )
    return {
        "org_name": org_name,
        "contact_number_with_country_code": target["contact_number_with_country_code"],
        "opening_line": (
            f"Hello, I'm calling on behalf of {client_name or 'our company'} "
            f"to verify compliance requirements with {org_name}."
        ),
        "speech": speech,
        "clarification_questions": questions[:5],
    }


def normalize_output(
    raw_output: dict,
    client_name: str,
    target_country: str,
    model: str,
    valid_targets: list[dict],
) -> dict:
    raw_speeches = raw_output.get("call_speeches", [])
    if not isinstance(raw_speeches, list):
        raw_speeches = []

    index = {}
    for item in raw_speeches:
        if not isinstance(item, dict):
            continue
        org = str(item.get("org_name") or "").strip().lower()
        phone = str(item.get("contact_number_with_country_code") or "").strip()
        if org and phone:
            index[(org, phone)] = item

    normalized = []
    for target in valid_targets:
        key = (
            target["org_name"].strip().lower(),
            target["contact_number_with_country_code"].strip(),
        )
        candidate = index.get(key)
        if not candidate:
            normalized.append(fallback_script(client_name, target))
            continue

        opening_line = str(candidate.get("opening_line") or "").strip()
        speech = str(candidate.get("speech") or "").strip()
        questions = candidate.get("clarification_questions", [])
        if isinstance(questions, str):
            questions = [questions.strip()] if questions.strip() else []
        elif isinstance(questions, list):
            questions = [str(x).strip() for x in questions if str(x).strip()]
        else:
            questions = []

        if not opening_line or not speech:
            normalized.append(fallback_script(client_name, target))
            continue

        normalized.append(
            {
                "org_name": target["org_name"],
                "contact_number_with_country_code": target[
                    "contact_number_with_country_code"
                ],
                "opening_line": opening_line,
                "speech": speech,
                "clarification_questions": questions[:6],
            }
        )

    return {
        "client_name": client_name,
        "target_country": target_country,
        "model": model,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "call_speeches": normalized,
    }


def generate_speeches_with_claude(
    api_key: str,
    model: str,
    client_name: str,
    target_country: str,
    valid_targets: list[dict],
) -> dict:
    system_prompt = (
        "You generate outbound call scripts for compliance verification. "
        "Return ONLY valid JSON with this exact schema: "
        "{"
        "\"call_speeches\": ["
        "{"
        "\"org_name\": string,"
        "\"contact_number_with_country_code\": string,"
        "\"opening_line\": string,"
        "\"speech\": string,"
        "\"clarification_questions\": [string]"
        "}"
        "]"
        "}. "
        "Rules: "
        "1) Generate one entry for each provided target. "
        "2) Keep each speech concise (80-140 words). "
        "3) Ask only practical questions from ask_and_clarify. "
        "4) No markdown, no code fences."
    )

    payload = {
        "client_name": client_name,
        "target_country": target_country,
        "targets": valid_targets,
    }

    last_error = None
    for attempt, retry_prefix in enumerate(
        [
            "",
            "Previous output was invalid JSON. Return shorter valid JSON only.",
        ],
        start=1,
    ):
        prompt = json.dumps(payload, ensure_ascii=False)
        if retry_prefix:
            prompt = f"{retry_prefix}\n\n{prompt}"

        response = requests.post(
            ANTHROPIC_API_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": 2400,
                "temperature": 0.2,
                "system": system_prompt,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()

        text_blocks = [
            block.get("text", "")
            for block in data.get("content", [])
            if block.get("type") == "text"
        ]
        raw_text = "\n".join(text_blocks)

        try:
            return extract_json(raw_text, required_keys=REQUIRED_RESPONSE_KEYS)
        except ValueError as exc:
            debug_path = Path("debug_create_speech_raw.txt")
            debug_path.write_text(raw_text, encoding="utf-8")
            last_error = (
                f"{exc}; stop_reason={data.get('stop_reason')}; "
                f"attempt={attempt}; raw_saved={debug_path}"
            )
            continue

    raise ValueError(last_error or "Model output could not be parsed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create call speech JSON from unsure-info call targets that have "
            "a non-null phone number."
        )
    )
    parser.add_argument(
        "--input-json",
        default="unsure_info.json",
        help="Path to unsure-info JSON input",
    )
    parser.add_argument(
        "--output-json",
        default="call_speeches.json",
        help="Output JSON path (generic by default)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Missing ANTHROPIC_API_KEY in environment or .env", file=sys.stderr)
        return 1

    input_path = Path(args.input_json)
    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 1

    client_name, target_country, valid_targets = load_call_targets(input_path)
    if not valid_targets:
        print(
            "No call_targets with non-null contact_number_with_country_code found.",
            file=sys.stderr,
        )
        return 1

    try:
        raw_output = generate_speeches_with_claude(
            api_key=api_key,
            model=config.anthropic_model,
            client_name=client_name or config.client_name,
            target_country=target_country or config.target_country,
            valid_targets=valid_targets,
        )
    except requests.HTTPError as exc:
        body = exc.response.text if exc.response is not None else ""
        print(f"Claude API request failed: {exc}\n{body}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Failed to parse Claude output: {exc}", file=sys.stderr)
        return 1

    output = normalize_output(
        raw_output=raw_output,
        client_name=client_name or config.client_name,
        target_country=target_country or config.target_country,
        model=config.anthropic_model,
        valid_targets=valid_targets,
    )
    output_json = json.dumps(output, indent=2, ensure_ascii=False)
    print(output_json)

    output_path = Path(args.output_json)
    output_path.write_text(output_json + "\n", encoding="utf-8")
    print(f"Saved speech JSON to: {output_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
