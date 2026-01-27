import uuid
from .coqui_tts import generate_tts_with_coqui
from .elevenlabs_tts import generate_tts_with_elevenlabs

def clean_text(text):
    return (text.replace("’", "'")
                .replace("‘", "'")
                .replace("“", '"')
                .replace("”", '"')
                .replace("\u200b", '')
                .strip())
def text_to_podcast(script, emotion):
    unique_id = uuid.uuid4().hex[:8]
    script = clean_text(script)

    try:
        temp_voice_path = f"temp_voice_{unique_id}.wav"
        voice_path = generate_tts_with_elevenlabs(script, temp_voice_path)
        print("TTS generation completed. Passing voice to mixer...")
        return voice_path   # return temp file path only
    except Exception as e:
        print(f"ElevenLabs failed: {e}")
        print("Falling back to Coqui TTS...")

        temp_voice_path = f"temp_voice_{unique_id}.wav"
        voice_path = generate_tts_with_coqui(script, temp_voice_path)
        print("TTS generation completed. Passing voice to mixer...")
        return voice_path
