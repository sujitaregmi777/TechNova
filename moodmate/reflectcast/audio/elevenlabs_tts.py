import requests
from dotenv import load_dotenv
import os
from ..config import ELEVENLABS_API_KEY

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

def generate_tts_with_elevenlabs(script, output_path="outputs/elevenlabs_voice.wav"):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": script,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.7,
             "style": 0.3,         # lower = more gentle
            "speed": 0.85         # the voice to 85% speed
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        return output_path
    else:
        raise Exception(f"ElevenLabs API Error: {response.status_code} - {response.text}")