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
REQUIRED_KEYS = ["client_name", "target_country", "call_targets"]


def extract_json(text: str, required_keys: list[str] | None = None) -> dict:
    raw = text.strip()
    if not raw:
        raise ValueError("Model returned an empty response.")

    candidates: list[str] = [raw]
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

    raise ValueError("Could not parse a valid JSON object from model response.")


def normalize_call_targets(payload: dict) -> dict:
    targets = payload.get("call_targets")
    if not isinstance(targets, list):
        targets = []

    normalized_targets = []
    for item in targets:
        if not isinstance(item, dict):
            continue
        org_name = str(item.get("org_name") or "").strip()
        if not org_name:
            continue

        contact_number = item.get("contact_number_with_country_code")
        country_code = item.get("country_code")
        ask = item.get("ask_and_clarify")
        source_urls = item.get("source_urls")

        if isinstance(ask, str):
            ask_list = [ask.strip()] if ask.strip() else []
        elif isinstance(ask, list):
            ask_list = [str(x).strip() for x in ask if str(x).strip()]
        else:
            ask_list = []

        if isinstance(source_urls, str):
            source_list = [source_urls.strip()] if source_urls.strip() else []
        elif isinstance(source_urls, list):
            source_list = [str(x).strip() for x in source_urls if str(x).strip()]
        else:
            source_list = []

        normalized_targets.append(
            {
                "org_name": org_name,
                "contact_number_with_country_code": (
                    str(contact_number).strip() if contact_number else None
                ),
                "country_code": str(country_code).strip() if country_code else None,
                "ask_and_clarify": ask_list,
                "source_urls": source_list,
            }
        )

    return {
        "client_name": str(payload.get("client_name") or "").strip(),
        "target_country": str(payload.get("target_country") or "").strip(),
        "call_targets": normalized_targets,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def load_follow_up_inputs(path: Path) -> dict:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        "client_name": raw.get("client_name"),
        "target_country": raw.get("target_country"),
        "unclear_or_unsure": raw.get("unclear_or_unsure", []),
        "possibly_outdated": raw.get("possibly_outdated", []),
        "follow_up_research_queries": raw.get("follow_up_research_queries", []),
    }


def call_claude_for_call_targets(api_key: str, model: str, follow_up_input: dict) -> dict:
    system_prompt = (
        "You are a compliance follow-up research agent. "
        "Use web search to identify which organizations should be called to clarify open issues. "
        "Return ONLY valid JSON with this exact schema: "
        "{"
        "\"client_name\": string,"
        "\"target_country\": string,"
        "\"call_targets\": ["
        "{"
        "\"org_name\": string,"
        "\"contact_number_with_country_code\": string|null,"
        "\"country_code\": string|null,"
        "\"ask_and_clarify\": [string],"
        "\"source_urls\": [string]"
        "}"
        "]"
        "}. "
        "Rules: "
        "1) Prefer official entities (government agencies, regulators, municipalities, official business portals). "
        "2) Phone number must include country code (example: +46...). "
        "3) If number is not found reliably, set it to null. "
        "4) Keep ask_and_clarify practical and specific to unclear/outdated topics. "
        "5) Keep response compact. Maximum 8 organizations."
    )

    user_prompt = (
        "Build a phone outreach list from this follow-up context:\n"
        f"{json.dumps(follow_up_input, ensure_ascii=False)}"
    )

    last_error = None
    for attempt, retry_prefix in enumerate(
        [
            "",
            "Previous response was invalid or incomplete JSON. Return shorter valid JSON only.",
        ],
        start=1,
    ):
        content = user_prompt if not retry_prefix else f"{retry_prefix}\n\n{user_prompt}"

        response = requests.post(
            ANTHROPIC_API_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": 2200,
                "temperature": 0.2,
                "system": system_prompt,
                "messages": [{"role": "user", "content": content}],
                "tools": [
                    {
                        "type": "web_search_20250305",
                        "name": "web_search",
                        "max_uses": 4 if attempt == 1 else 2,
                    }
                ],
            },
            timeout=150,
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
            return extract_json(raw_text, required_keys=REQUIRED_KEYS)
        except ValueError as exc:
            debug_path = Path("debug_unsure_info_raw.txt")
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
            "Read unclear/outdated follow-up items and produce a call-target JSON "
            "with org names, phone numbers, and questions to clarify."
        )
    )
    parser.add_argument(
        "--input-json",
        default="research.json",
        help="Input research JSON path (default: research.json)",
    )
    parser.add_argument(
        "--output-json",
        default="unsure_info.json",
        help="Output path for call target JSON (default: unsure_info.json)",
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

    follow_up_input = load_follow_up_inputs(input_path)
    if not any(
        [
            follow_up_input.get("unclear_or_unsure"),
            follow_up_input.get("possibly_outdated"),
            follow_up_input.get("follow_up_research_queries"),
        ]
    ):
        print("No follow-up items found in input JSON.", file=sys.stderr)
        return 1

    try:
        raw_payload = call_claude_for_call_targets(
            api_key=api_key,
            model=config.anthropic_model,
            follow_up_input=follow_up_input,
        )
    except requests.HTTPError as exc:
        body = exc.response.text if exc.response is not None else ""
        print(f"Claude API request failed: {exc}\n{body}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Failed to parse Claude output: {exc}", file=sys.stderr)
        return 1

    output = normalize_call_targets(raw_payload)
    if not output["client_name"]:
        output["client_name"] = config.client_name
    if not output["target_country"]:
        output["target_country"] = config.target_country
    output["model"] = config.anthropic_model

    output_json = json.dumps(output, indent=2, ensure_ascii=False)
    print(output_json)

    output_path = Path(args.output_json)
    output_path.write_text(output_json + "\n", encoding="utf-8")
    print(f"Saved unsure-info JSON to: {output_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
