# gt_track

Lightweight AI calling pipeline for:
1. compliance research,
2. follow-up target discovery,
3. call-script generation,
4. outbound call execution,
5. transcript capture,
6. booking detection + optional Google Calendar event creation.

## Quick start

1. Create env file:
```bash
cp .env.example .env
```
2. Fill required values in `.env` (`ANTHROPIC_API_KEY`, `ELEVENLABS_*`, `TO_NUMBER`, etc.).
3. Install Python deps:
```bash
python3 -m pip install requests python-dotenv
```

Optional deps:
- Better phone/country detection:
```bash
python3 -m pip install phonenumbers
```
- Google Calendar event creation (`booking.py --create-event`):
```bash
python3 -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Main run

Run full pipeline:
```bash
python3 run_pipeline.py
```

Current behavior:
- It discovers all target numbers from generated research.
- It **dials only `TO_NUMBER`** from `.env` (demo-safe mode).
- It stores state in `pipeline_state.json`.
- It stores per-run artifacts in `pipeline_runs/run_<timestamp>/`.

## Step-by-step flow

The scripted order is:
1. `web_research.py`
2. `unsure_info.py`
3. `create_speech.py`
4. `make_call.py` / outbound call logic in `run_pipeline.py`
5. `get_transcript.py`
6. `booking.py`

See also: `workflow_order.txt`.

## Key generated files

- `research.json`
- `unsure_info.json`
- `call_speeches.json`
- `transcript.json` (latest transcript copy)
- `pipeline_state.json` (latest run state)
- `pipeline_runs/` (all run logs/artifacts)

## Notes

- `.env` and generated artifacts are gitignored.
- Use `.env.example` to share required configuration with teammates.
