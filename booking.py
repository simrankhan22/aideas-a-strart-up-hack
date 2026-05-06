import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests
from dotenv import load_dotenv

from config_app import load_config


CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar"]
DEFAULT_GUEST_EMAILS = ["dio.pizarro@gmail.com"]


def parse_transcript_file(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()

    metadata: dict[str, str] = {}
    transcript_lines: list[str] = []
    in_transcript = False

    for line in lines:
        if not in_transcript and line.strip().lower() == "transcript:":
            in_transcript = True
            continue

        if in_transcript:
            transcript_lines.append(line)
            continue

        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip().lower()] = value.strip()

    transcript_text = "\n".join(transcript_lines).strip()
    return metadata, transcript_text


def extract_json_from_text(text: str) -> dict:
    text = text.strip()
    if not text:
        raise ValueError("Claude returned an empty response.")

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("Could not find JSON object in Claude response.")
        return json.loads(text[start : end + 1])


def evaluate_booking_with_claude(
    api_key: str,
    model: str,
    transcript_text: str,
    metadata: dict,
) -> dict:
    timezone_name = get_timezone(metadata)
    timezone_hint = metadata.get("timezone", timezone_name)
    country_hint = metadata.get("country", "unknown")
    called_number = metadata.get("called number", "unknown")
    reference_now_local = dt.datetime.now(ZoneInfo(timezone_name))

    system_prompt = (
        "You are a strict call QA evaluator. "
        "Decide if a booking/meeting was explicitly agreed in the transcript. "
        "Return ONLY valid JSON with this exact schema: "
        "{\"booking_agreed\": boolean, "
        "\"meeting_name\": string|null, "
        "\"meeting_day\": string|null, "
        "\"meeting_time\": string|null}. "
        "Rules: "
        "1) booking_agreed=true only when both sides clearly commit to a meeting/booking. "
        "2) Suggestions like 'we should schedule' without commitment are NOT agreement. "
        "3) If booking_agreed=false, set meeting_name/day/time to null. "
        "4) If booking_agreed=true but one detail is missing, set only missing details to null. "
        "5) Resolve relative dates/times (e.g., tomorrow, next Thursday) using the provided "
        "reference local datetime and timezone. "
        "6) meeting_day should be YYYY-MM-DD when derivable; otherwise null. "
        "7) meeting_time should be HH:MM (24-hour) local time when derivable; otherwise null."
    )

    user_payload = {
        "timezone_hint": timezone_hint,
        "timezone_reference": timezone_name,
        "country_hint": country_hint,
        "called_number": called_number,
        "reference_datetime_local": reference_now_local.isoformat(),
        "reference_date_local": reference_now_local.strftime("%Y-%m-%d"),
        "reference_weekday_local": reference_now_local.strftime("%A"),
        "transcript": transcript_text,
    }

    response = requests.post(
        CLAUDE_API_URL,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": 600,
            "temperature": 0,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(user_payload, ensure_ascii=False),
                        }
                    ],
                }
            ],
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()

    text_chunks = []
    for block in data.get("content", []):
        if block.get("type") == "text":
            text_chunks.append(block.get("text", ""))
    return extract_json_from_text("\n".join(text_chunks))


def normalize_result(raw: dict) -> dict:
    booking_agreed = raw.get("booking_agreed")
    if isinstance(booking_agreed, bool):
        agreed = booking_agreed
    elif isinstance(booking_agreed, str):
        agreed = booking_agreed.strip().lower() in {"true", "yes", "1"}
    else:
        agreed = False

    def clean_value(value) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            text = value.strip()
            if not text or text.lower() in {"null", "none", "n/a", "unknown"}:
                return None
            return text
        return str(value)

    normalized = {
        "booking_agreed": agreed,
        "meeting_name": clean_value(raw.get("meeting_name")),
        "meeting_day": clean_value(raw.get("meeting_day")),
        "meeting_time": clean_value(raw.get("meeting_time")),
    }

    if not normalized["booking_agreed"]:
        normalized["meeting_name"] = None
        normalized["meeting_day"] = None
        normalized["meeting_time"] = None

    return normalized


def get_timezone(metadata: dict) -> str:
    timezone_value = (metadata.get("timezone") or "UTC").strip()
    if "," in timezone_value:
        timezone_value = timezone_value.split(",", 1)[0].strip()
    try:
        ZoneInfo(timezone_value)
        return timezone_value
    except ZoneInfoNotFoundError:
        return "UTC"


def parse_start_datetime(meeting_day: str, meeting_time: str, timezone_name: str) -> dt.datetime:
    date_obj = dt.datetime.strptime(meeting_day, "%Y-%m-%d").date()

    time_formats = ("%H:%M", "%H:%M:%S", "%I:%M %p", "%I %p", "%I%p")
    parsed_time = None
    for time_format in time_formats:
        try:
            parsed_time = dt.datetime.strptime(meeting_time.strip(), time_format).time()
            break
        except ValueError:
            continue

    if parsed_time is None:
        raise ValueError(
            "meeting_time must be parseable as HH:MM (24h) or common AM/PM format."
        )

    return dt.datetime.combine(date_obj, parsed_time, tzinfo=ZoneInfo(timezone_name))


def load_calendar_service(token_path: Path, credentials_path: Path):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError(
            "Missing Google Calendar dependencies. Install: "
            "python3 -m pip install --upgrade google-api-python-client "
            "google-auth-httplib2 google-auth-oauthlib"
        ) from exc

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), CALENDAR_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                raise RuntimeError(
                    f"Missing credentials file for OAuth flow: {credentials_path}"
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path),
                CALENDAR_SCOPES,
            )
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")

    return build("calendar", "v3", credentials=creds)


def maybe_create_calendar_event(
    result: dict,
    metadata: dict,
    token_path: Path,
    credentials_path: Path,
    calendar_id: str,
    duration_minutes: int,
    guest_emails: list[str],
) -> None:
    if not result["booking_agreed"]:
        print("No booking agreed, skipping calendar event creation.", file=sys.stderr)
        return

    meeting_name = result.get("meeting_name")
    meeting_day = result.get("meeting_day")
    meeting_time = result.get("meeting_time")
    if not meeting_day or not meeting_time:
        raise RuntimeError(
            "Booking is agreed but missing meeting_day or meeting_time, cannot create event."
        )

    timezone_name = get_timezone(metadata)
    start_dt = parse_start_datetime(meeting_day, meeting_time, timezone_name)
    end_dt = start_dt + dt.timedelta(minutes=duration_minutes)

    service = load_calendar_service(token_path=token_path, credentials_path=credentials_path)
    event_payload = {
        "summary": meeting_name or "Meeting",
        "start": {"dateTime": start_dt.isoformat(), "timeZone": timezone_name},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": timezone_name},
        "attendees": [{"email": email} for email in guest_emails],
        "conferenceData": {
            "createRequest": {
                "requestId": f"booking-{uuid4().hex}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
    }
    created = (
        service.events()
        .insert(
            calendarId=calendar_id,
            body=event_payload,
            conferenceDataVersion=1,
            sendUpdates="all",
        )
        .execute()
    )
    html_link = created.get("htmlLink")
    meet_link = created.get("hangoutLink")
    if not meet_link:
        entry_points = (
            created.get("conferenceData", {}).get("entryPoints", [])
            if isinstance(created.get("conferenceData"), dict)
            else []
        )
        for entry in entry_points:
            if entry.get("entryPointType") == "video" and entry.get("uri"):
                meet_link = entry["uri"]
                break

    print(
        f"Calendar event created: {html_link or created.get('id', 'unknown')}",
        file=sys.stderr,
    )
    print(f"Google Meet link: {meet_link or 'not available'}", file=sys.stderr)
    print(f"Invited guests: {', '.join(guest_emails)}", file=sys.stderr)


def main() -> int:
    app_config = load_config()

    parser = argparse.ArgumentParser(
        description=(
            "Read a transcript .txt and use Claude API to evaluate whether "
            "a booking was agreed."
        )
    )
    parser.add_argument("transcript_path", help="Path to transcript .txt file")
    parser.add_argument(
        "--model",
        default=app_config.anthropic_model,
        help=f"Claude model name (default from config_app.anthropic_model: {app_config.anthropic_model})",
    )
    parser.add_argument(
        "--output-json",
        default=None,
        help="Optional path to save evaluation JSON",
    )
    parser.add_argument(
        "--create-event",
        action="store_true",
        help="Create Google Calendar event when booking_agreed is true.",
    )
    parser.add_argument(
        "--calendar-id",
        default="primary",
        help="Target Google Calendar ID (default: primary)",
    )
    parser.add_argument(
        "--duration-minutes",
        type=int,
        default=30,
        help="Event duration in minutes (default: 30)",
    )
    parser.add_argument(
        "--token-path",
        default="token.json",
        help="Path to Google OAuth token file (default: token.json)",
    )
    parser.add_argument(
        "--credentials-path",
        default="credentials.json",
        help="Path to Google OAuth client credentials (default: credentials.json)",
    )
    parser.add_argument(
        "--guest-email",
        action="append",
        default=None,
        help=(
            "Guest email to invite. Repeat for multiple guests. "
            "Default: dio.pizarro@gmail.com"
        ),
    )
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Missing ANTHROPIC_API_KEY in environment or .env", file=sys.stderr)
        return 1

    transcript_path = Path(args.transcript_path)
    if not transcript_path.exists():
        print(f"Transcript file not found: {transcript_path}", file=sys.stderr)
        return 1

    metadata, transcript_text = parse_transcript_file(transcript_path)
    if not transcript_text:
        print("Transcript text is empty.", file=sys.stderr)
        return 1

    try:
        result = evaluate_booking_with_claude(
            api_key=api_key,
            model=args.model,
            transcript_text=transcript_text,
            metadata=metadata,
        )
    except requests.HTTPError as exc:
        body = exc.response.text if exc.response is not None else ""
        print(f"Claude API request failed: {exc}\n{body}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Failed to parse Claude response: {exc}", file=sys.stderr)
        return 1

    result = normalize_result(result)
    result_json = json.dumps(result, indent=2, ensure_ascii=False)
    print(result_json)

    if args.output_json:
        output_path = Path(args.output_json)
        output_path.write_text(result_json + "\n", encoding="utf-8")

    if args.create_event:
        if args.duration_minutes <= 0:
            print("--duration-minutes must be > 0", file=sys.stderr)
            return 1
        guest_emails = args.guest_email if args.guest_email else DEFAULT_GUEST_EMAILS
        try:
            maybe_create_calendar_event(
                result=result,
                metadata=metadata,
                token_path=Path(args.token_path),
                credentials_path=Path(args.credentials_path),
                calendar_id=args.calendar_id,
                duration_minutes=args.duration_minutes,
                guest_emails=guest_emails,
            )
        except Exception as exc:
            print(f"Calendar event creation failed: {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
