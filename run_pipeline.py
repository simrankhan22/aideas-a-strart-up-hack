import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from config_app import load_config


ELEVENLABS_OUTBOUND_URL = "https://api.elevenlabs.io/v1/convai/twilio/outbound-call"
DEMO_GUEST_EMAIL = "dio.pizarro@gmail.com"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_e164(phone: str | None) -> str | None:
    if not phone:
        return None
    text = str(phone).strip()
    if not text:
        return None
    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return None
    normalized = f"+{digits}"
    if not re.fullmatch(r"\+\d{7,15}", normalized):
        return None
    return normalized


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def save_state(state: dict, state_path: Path, run_state_path: Path) -> None:
    write_json(state_path, state)
    write_json(run_state_path, state)


def run_script(
    script: str,
    script_args: list[str],
    cwd: Path,
    env: dict[str, str],
) -> tuple[str, str]:
    cmd = [sys.executable, str(cwd / script), *script_args]
    process = subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env,
        text=True,
        capture_output=True,
    )
    if process.returncode != 0:
        raise RuntimeError(
            f"{script} failed with code {process.returncode}\n"
            f"STDOUT:\n{process.stdout}\n"
            f"STDERR:\n{process.stderr}"
        )
    return process.stdout, process.stderr


def ensure_required_env_vars(names: list[str]) -> None:
    missing = [name for name in names if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


def load_call_speeches(path: Path, max_targets: int | None) -> list[dict]:
    payload = read_json(path)
    speeches = payload.get("call_speeches", [])
    if not isinstance(speeches, list):
        raise RuntimeError(f"Invalid call_speeches format in {path}")

    targets: list[dict] = []
    seen = set()
    for item in speeches:
        if not isinstance(item, dict):
            continue
        org_name = str(item.get("org_name") or "").strip()
        phone = normalize_e164(item.get("contact_number_with_country_code"))
        if not org_name or not phone:
            continue
        key = (org_name.lower(), phone)
        if key in seen:
            continue
        seen.add(key)
        targets.append(
            {
                "org_name": org_name,
                "phone": phone,
                "opening_line": str(item.get("opening_line") or "").strip(),
                "speech": str(item.get("speech") or "").strip(),
                "clarification_questions": (
                    item.get("clarification_questions")
                    if isinstance(item.get("clarification_questions"), list)
                    else []
                ),
            }
        )

    if max_targets is not None:
        return targets[:max_targets]
    return targets


def place_outbound_call(
    session: requests.Session,
    api_key: str,
    agent_id: str,
    phone_number_id: str,
    target: dict,
    include_dynamic_variables: bool,
) -> dict:
    payload: dict[str, Any] = {
        "agent_id": agent_id,
        "agent_phone_number_id": phone_number_id,
        "to_number": target["phone"],
    }

    if include_dynamic_variables:
        payload["conversation_initiation_client_data"] = {
            "dynamic_variables": {
                "org_name": target.get("org_name"),
                "call_opening_line": target.get("opening_line"),
                "call_speech": target.get("speech"),
                "call_questions_json": json.dumps(target.get("clarification_questions", [])),
            }
        }

    response = session.post(
        ELEVENLABS_OUTBOUND_URL,
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=45,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"ElevenLabs call failed [{response.status_code}]: {response.text}")
    return response.json()


def place_outbound_call_with_retry(
    session: requests.Session,
    api_key: str,
    agent_id: str,
    phone_number_id: str,
    target: dict,
    max_attempts: int,
) -> tuple[dict, int]:
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            return (
                place_outbound_call(
                    session=session,
                    api_key=api_key,
                    agent_id=agent_id,
                    phone_number_id=phone_number_id,
                    target=target,
                    include_dynamic_variables=True,
                ),
                attempt,
            )
        except Exception as first_exc:
            last_error = first_exc
            try:
                return (
                    place_outbound_call(
                        session=session,
                        api_key=api_key,
                        agent_id=agent_id,
                        phone_number_id=phone_number_id,
                        target=target,
                        include_dynamic_variables=False,
                    ),
                    attempt,
                )
            except Exception as second_exc:
                last_error = second_exc
                if attempt < max_attempts:
                    time.sleep(2)
                    continue

    raise RuntimeError(str(last_error) if last_error else "Unknown call error")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the end-to-end pipeline: web_research -> unsure_info -> "
            "create_speech -> outbound calls -> transcript -> booking."
        )
    )
    parser.add_argument("--state-json", default="pipeline_state.json")
    parser.add_argument("--max-targets", type=int, default=None)
    parser.add_argument("--max-call-attempts", type=int, default=2)
    parser.add_argument("--poll-seconds", type=int, default=3)
    parser.add_argument("--timeout-seconds", type=int, default=420)
    parser.add_argument("--stop-on-booking", action="store_true")
    parser.add_argument("--skip-research", action="store_true")
    parser.add_argument("--skip-unsure-info", action="store_true")
    parser.add_argument("--skip-create-speech", action="store_true")
    parser.add_argument("--calendar-id", default="primary")
    parser.add_argument("--duration-minutes", type=int, default=30)
    parser.add_argument("--token-path", default="token.json")
    parser.add_argument("--credentials-path", default="credentials.json")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = Path(__file__).resolve().parent
    load_dotenv(dotenv_path=root / ".env")
    app_config = load_config()

    ensure_required_env_vars(
        [
            "ANTHROPIC_API_KEY",
            "ELEVENLABS_API_KEY",
            "ELEVENLABS_AGENT_ID",
            "ELEVENLABS_PHONE_NUMBER_ID",
            "TO_NUMBER",
        ]
    )

    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%d_%H%M%S")
    run_dir = root / "pipeline_runs" / run_id
    transcripts_dir = run_dir / "transcripts"
    bookings_dir = run_dir / "bookings"
    run_dir.mkdir(parents=True, exist_ok=True)
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    bookings_dir.mkdir(parents=True, exist_ok=True)

    state_path = root / args.state_json
    run_state_path = run_dir / "state.json"

    state: dict[str, Any] = {
        "run_id": run_id,
        "started_at_utc": utc_now(),
        "config": {
            "client_name": app_config.client_name,
            "client_business": app_config.client_business,
            "target_country": app_config.target_country,
            "anthropic_model": app_config.anthropic_model,
        },
        "steps": {
            "web_research": {"status": "pending"},
            "unsure_info": {"status": "pending"},
            "create_speech": {"status": "pending"},
            "targets_discovered": [],
            "calls": [],
        },
        "summary": {
            "targets_total": 0,
            "targets_skipped_not_called": 0,
            "calls_planned": 0,
            "calls_completed": 0,
            "calls_failed": 0,
            "bookings_agreed": 0,
        },
    }
    save_state(state, state_path, run_state_path)

    env = os.environ.copy()
    session = requests.Session()

    try:
        if not args.skip_research:
            state["steps"]["web_research"] = {"status": "running", "started_at_utc": utc_now()}
            save_state(state, state_path, run_state_path)
            run_script(
                "web_research.py",
                ["--output-json", "research.json"],
                cwd=root,
                env=env,
            )
            state["steps"]["web_research"] = {
                "status": "completed",
                "completed_at_utc": utc_now(),
                "output_file": "research.json",
            }
            save_state(state, state_path, run_state_path)
        else:
            state["steps"]["web_research"] = {"status": "skipped"}
            save_state(state, state_path, run_state_path)

        if not args.skip_unsure_info:
            state["steps"]["unsure_info"] = {"status": "running", "started_at_utc": utc_now()}
            save_state(state, state_path, run_state_path)
            run_script(
                "unsure_info.py",
                ["--input-json", "research.json", "--output-json", "unsure_info.json"],
                cwd=root,
                env=env,
            )
            state["steps"]["unsure_info"] = {
                "status": "completed",
                "completed_at_utc": utc_now(),
                "input_file": "research.json",
                "output_file": "unsure_info.json",
            }
            save_state(state, state_path, run_state_path)
        else:
            state["steps"]["unsure_info"] = {"status": "skipped"}
            save_state(state, state_path, run_state_path)

        if not args.skip_create_speech:
            state["steps"]["create_speech"] = {
                "status": "running",
                "started_at_utc": utc_now(),
            }
            save_state(state, state_path, run_state_path)
            run_script(
                "create_speech.py",
                ["--input-json", "unsure_info.json", "--output-json", "call_speeches.json"],
                cwd=root,
                env=env,
            )
            state["steps"]["create_speech"] = {
                "status": "completed",
                "completed_at_utc": utc_now(),
                "input_file": "unsure_info.json",
                "output_file": "call_speeches.json",
            }
            save_state(state, state_path, run_state_path)
        else:
            state["steps"]["create_speech"] = {"status": "skipped"}
            save_state(state, state_path, run_state_path)

        targets = load_call_speeches(root / "call_speeches.json", args.max_targets)
        state["summary"]["targets_total"] = len(targets)
        state["steps"]["targets_discovered"] = [
            {
                "index": idx,
                "org_name": target["org_name"],
                "phone": target["phone"],
            }
            for idx, target in enumerate(targets, start=1)
        ]
        save_state(state, state_path, run_state_path)
        if not targets:
            raise RuntimeError("No valid call targets found in call_speeches.json")

        to_number = normalize_e164(os.environ["TO_NUMBER"])
        if not to_number:
            raise RuntimeError("Invalid TO_NUMBER in .env. It must be valid E.164 format.")

        # Trial-safe mode: call only one number (TO_NUMBER), but keep all discovered target phones in state.
        target = dict(targets[0])
        original_target_phone = target["phone"]
        target["phone"] = to_number
        call_plan = [target]
        state["summary"]["calls_planned"] = len(call_plan)
        state["summary"]["targets_skipped_not_called"] = max(0, len(targets) - len(call_plan))
        save_state(state, state_path, run_state_path)

        api_key = os.environ["ELEVENLABS_API_KEY"]
        agent_id = os.environ["ELEVENLABS_AGENT_ID"]
        phone_number_id = os.environ["ELEVENLABS_PHONE_NUMBER_ID"]

        for index, target in enumerate(call_plan, start=1):
            target_state: dict[str, Any] = {
                "index": index,
                "org_name": target["org_name"],
                "target_phone": original_target_phone,
                "dial_phone": target["phone"],
                "status": "running",
                "started_at_utc": utc_now(),
            }
            state["steps"]["calls"].append(target_state)
            save_state(state, state_path, run_state_path)

            try:
                call_response, attempts = place_outbound_call_with_retry(
                    session=session,
                    api_key=api_key,
                    agent_id=agent_id,
                    phone_number_id=phone_number_id,
                    target=target,
                    max_attempts=max(1, args.max_call_attempts),
                )
                conversation_id = str(call_response.get("conversation_id") or "").strip()
                if not conversation_id:
                    raise RuntimeError(
                        f"Missing conversation_id in ElevenLabs response: {call_response}"
                    )

                target_state["attempts"] = attempts
                target_state["conversation_id"] = conversation_id
                target_state["call_response"] = call_response
                save_state(state, state_path, run_state_path)

                transcript_path = transcripts_dir / f"transcript_{index:02d}_{conversation_id}.json"
                run_script(
                    "get_transcript.py",
                    [
                        conversation_id,
                        "--output-json",
                        str(transcript_path),
                        "--poll-seconds",
                        str(args.poll_seconds),
                        "--timeout-seconds",
                        str(args.timeout_seconds),
                    ],
                    cwd=root,
                    env=env,
                )
                shutil.copyfile(transcript_path, root / "transcript.json")

                booking_path = bookings_dir / f"booking_{index:02d}_{conversation_id}.json"
                booking_args = [
                    str(transcript_path),
                    "--output-json",
                    str(booking_path),
                    "--create-event",
                    "--calendar-id",
                    args.calendar_id,
                    "--duration-minutes",
                    str(args.duration_minutes),
                    "--token-path",
                    args.token_path,
                    "--credentials-path",
                    args.credentials_path,
                    "--guest-email",
                    DEMO_GUEST_EMAIL,
                ]

                run_script("booking.py", booking_args, cwd=root, env=env)
                booking_result = read_json(booking_path)

                target_state["status"] = "completed"
                target_state["completed_at_utc"] = utc_now()
                target_state["transcript_file"] = str(transcript_path.relative_to(root))
                target_state["booking_file"] = str(booking_path.relative_to(root))
                target_state["booking_result"] = booking_result

                state["summary"]["calls_completed"] += 1
                if booking_result.get("booking_agreed"):
                    state["summary"]["bookings_agreed"] += 1

                save_state(state, state_path, run_state_path)

                if args.stop_on_booking and booking_result.get("booking_agreed"):
                    break

            except Exception as exc:
                target_state["status"] = "failed"
                target_state["failed_at_utc"] = utc_now()
                target_state["error"] = str(exc)
                state["summary"]["calls_failed"] += 1
                save_state(state, state_path, run_state_path)

        state["finished_at_utc"] = utc_now()
        save_state(state, state_path, run_state_path)
        print(json.dumps(state["summary"], indent=2, ensure_ascii=False))
        print(f"Run state saved to: {state_path}")
        print(f"Run artifacts directory: {run_dir}")
        return 0

    except Exception as exc:
        state["finished_at_utc"] = utc_now()
        state["error"] = str(exc)
        save_state(state, state_path, run_state_path)
        print(f"Pipeline failed: {exc}", file=sys.stderr)
        print(f"State saved to: {state_path}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
