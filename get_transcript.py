import argparse
import os
import sys
import time

import requests
from dotenv import load_dotenv


BASE_URL = "https://api.elevenlabs.io/v1/convai"
FALLBACK_CALLING_CODE_DATA = {
    "1": ("United States/Canada", "US/CA", "America/New_York"),
    "33": ("France", "FR", "Europe/Paris"),
    "34": ("Spain", "ES", "Europe/Madrid"),
    "39": ("Italy", "IT", "Europe/Rome"),
    "44": ("United Kingdom", "GB", "Europe/London"),
    "45": ("Denmark", "DK", "Europe/Copenhagen"),
    "46": ("Sweden", "SE", "Europe/Stockholm"),
    "47": ("Norway", "NO", "Europe/Oslo"),
    "49": ("Germany", "DE", "Europe/Berlin"),
    "61": ("Australia", "AU", "Australia/Sydney"),
    "64": ("New Zealand", "NZ", "Pacific/Auckland"),
}


def fetch_conversation(session: requests.Session, conversation_id: str) -> dict:
    response = session.get(
        f"{BASE_URL}/conversations/{conversation_id}",
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def wait_until_finished(
    session: requests.Session,
    conversation_id: str,
    poll_seconds: int,
    timeout_seconds: int,
) -> dict:
    start = time.time()
    while True:
        conversation = fetch_conversation(session, conversation_id)
        status = conversation.get("status")
        if status in {"done", "failed"}:
            return conversation

        if time.time() - start > timeout_seconds:
            raise TimeoutError(
                f"Timed out waiting for conversation {conversation_id} to finish. "
                f"Last status: {status}"
            )

        time.sleep(poll_seconds)


def format_transcript(transcript: list[dict]) -> str:
    lines = []
    for turn in transcript:
        role = (turn.get("role") or "unknown").upper()
        secs = turn.get("time_in_call_secs")
        message = turn.get("message", "").strip()
        prefix = f"[{secs}s] " if secs is not None else ""
        lines.append(f"{prefix}{role}: {message}")
    return "\n".join(lines)


def extract_called_number(conversation: dict) -> str | None:
    metadata = conversation.get("metadata", {})
    phone_call = metadata.get("phone_call", {})
    dynamic_vars = (
        conversation.get("conversation_initiation_client_data", {})
        .get("dynamic_variables", {})
    )
    candidates = [
        phone_call.get("external_number"),
        dynamic_vars.get("system__called_number"),
        conversation.get("user_id"),
    ]
    for number in candidates:
        if isinstance(number, str) and number.strip():
            return number.strip()
    return None


def infer_phone_context(called_number: str | None) -> dict:
    context = {
        "called_number": called_number or "unknown",
        "country_calling_code": "unknown",
        "country": "unknown",
        "country_iso": "unknown",
        "timezone": "unknown",
    }
    if not called_number:
        return context

    digits = "".join(ch for ch in called_number if ch.isdigit())
    if called_number.strip().startswith("+"):
        for length in (3, 2, 1):
            code = digits[:length]
            if code in FALLBACK_CALLING_CODE_DATA:
                country_name, country_iso, timezone_name = FALLBACK_CALLING_CODE_DATA[
                    code
                ]
                context["country_calling_code"] = f"+{code}"
                context["country"] = country_name
                context["country_iso"] = country_iso
                context["timezone"] = timezone_name
                break

    try:
        import phonenumbers
        from phonenumbers import geocoder
        from phonenumbers import timezone as phone_timezone
    except ImportError:
        return context

    try:
        parsed = phonenumbers.parse(called_number, None)
    except phonenumbers.NumberParseException:
        return context

    if parsed.country_code:
        context["country_calling_code"] = f"+{parsed.country_code}"

    country_iso = phonenumbers.region_code_for_number(parsed)
    if country_iso:
        context["country_iso"] = country_iso

    country_name = geocoder.description_for_number(parsed, "en")
    if country_name:
        context["country"] = country_name

    timezones = phone_timezone.time_zones_for_number(parsed)
    if timezones:
        context["timezone"] = ", ".join(timezones)

    return context


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch an ElevenLabs conversation transcript by conversation_id.",
    )
    parser.add_argument("conversation_id", help="Conversation ID (e.g. conv_...)")
    parser.add_argument(
        "--poll-seconds",
        type=int,
        default=3,
        help="Polling interval while waiting for completion (default: 3)",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=300,
        help="Max wait time for completion (default: 300)",
    )
    parser.add_argument(
        "--output-json",
        "--output-txt",
        dest="output_path",
        default="transcript.json",
        help=(
            "Path to save transcript output text "
            "(default: transcript.json)"
        ),
    )
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("Missing ELEVENLABS_API_KEY in environment or .env", file=sys.stderr)
        return 1

    session = requests.Session()
    session.headers.update(
        {
            "xi-api-key": api_key,
            "Content-Type": "application/json",
        }
    )

    try:
        conversation = wait_until_finished(
            session,
            args.conversation_id,
            poll_seconds=args.poll_seconds,
            timeout_seconds=args.timeout_seconds,
        )
    except requests.HTTPError as exc:
        print(f"API request failed: {exc}", file=sys.stderr)
        return 1
    except TimeoutError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    status = conversation.get("status")
    transcript = conversation.get("transcript", [])
    conversation_id = conversation.get("conversation_id", args.conversation_id)
    phone_context = infer_phone_context(extract_called_number(conversation))
    terminal_lines = [
        f"Conversation ID: {conversation_id}",
        f"Conversation status: {status}",
        f"Called number: {phone_context['called_number']}",
        f"Country calling code: {phone_context['country_calling_code']}",
        f"Country: {phone_context['country']}",
        f"Country ISO: {phone_context['country_iso']}",
        f"Timezone: {phone_context['timezone']}",
    ]

    if phone_context["timezone"] == "unknown":
        terminal_lines.append(
            "Timezone note: install phonenumbers for broader country/timezone detection."
        )

    if not transcript:
        terminal_lines.append("")
        terminal_lines.append("No transcript found yet.")
    else:
        terminal_lines.append("")
        terminal_lines.append("Transcript:")
        terminal_lines.append("")
        terminal_lines.append(format_transcript(transcript))

    terminal_output = "\n".join(terminal_lines)
    print(terminal_output)

    with open(args.output_path, "w", encoding="utf-8") as f:
        f.write(terminal_output + "\n")
    print(f"\nSaved transcript output to: {args.output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
