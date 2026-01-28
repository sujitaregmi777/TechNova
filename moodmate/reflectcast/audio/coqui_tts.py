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

    # Split text into sentence chunks
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    print(f"[Edge TTS] Total text chunks: {len(sentences)}")

    final_audio = AudioSegment.empty()

    # Generate per sentence (keeps your original structure)
    for idx, sentence in enumerate(sentences):
        temp_path = output_path.with_name(f"{output_path.stem}_{idx}.mp3")

        print(f"[Edge TTS] Synthesizing chunk {idx+1}/{len(sentences)}")

        try:
            # Run Edge TTS
            asyncio.run(_edge_generate(sentence, str(temp_path)))

            # Load audio safely
            chunk_audio = AudioSegment.from_file(str(temp_path), format="mp3")
            final_audio += chunk_audio

            time.sleep(0.05)

            if temp_path.exists():
                temp_path.unlink()

        except Exception as e:
            print(f"[Edge TTS] Error on chunk {idx}: {e}")

    # Export combined audio as WAV (same as your old Coqui output)
    print(f"[Edge TTS] Exporting final audio to: {output_path}")
    final_audio.export(str(output_path), format="wav")

    print("[Edge TTS] Audio generation complete!\n")

    return str(output_path)
