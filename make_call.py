import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = "https://api.elevenlabs.io/v1/convai/twilio/outbound-call"
headers = {
    "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
    "Content-Type": "application/json",
}
payload = {
    "agent_id": os.environ["ELEVENLABS_AGENT_ID"],
    "agent_phone_number_id": os.environ["ELEVENLABS_PHONE_NUMBER_ID"],
    "to_number": os.environ["TO_NUMBER"],  # E.164 format, e.g. +15551234567
}

resp = requests.post(url, headers=headers, json=payload, timeout=30)
print(resp.status_code, resp.text)
resp.raise_for_status()