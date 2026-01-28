"""
Edge-TTS audio generation module
Windows-safe version
"""

from pathlib import Path
from pydub import AudioSegment
import asyncio
import edge_tts
import time
import uuid

# -----------------------------
# Voice selection
# -----------------------------
VOICE = "en-US-AriaNeural"

print("Edge TTS ready (no heavy model loading required).")

# -----------------------------
# Internal async generator
# -----------------------------
async def _edge_generate(text, output_path):
    communicate = edge_tts.Communicate(text=text, voice=VOICE)
    await communicate.save(output_path)

# -----------------------------
# Main generation function
# -----------------------------
def generate_tts_with_coqui(text, output_path=None):
    """
    Generate TTS audio from text using Edge TTS with sentence chunking.
    Returns final wav file path as string.
    """

    unique_id = uuid.uuid4().hex[:8]

    if output_path is None:
        output_path = Path("media/podcasts") / f"voice_{unique_id}.wav"
    else:
        output_path = Path(output_path)

    print("\n[Edge TTS] Starting audio generation...")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(_edge_generate(text, str(output_path)))
    print("[Edge TTS] Audio generation complete!\n")

    return str(output_path)
