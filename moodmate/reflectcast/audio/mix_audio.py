import uuid
import os
from pydub import AudioSegment
from django.conf import settings

AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\ffmpeg\bin\ffprobe.exe"


def mix_voice_with_ambient(voice_path, mood, podcast_id):
    print(f"Mixing ambient sound for mood: {mood}")
    mood = mood.lower()
    PROJECT_ROOT = settings.BASE_DIR
    ambient_map = {
        "overwhelmed": os.path.join(PROJECT_ROOT, "assets/ambient/overwhelmed.mp3"),
        "sad": os.path.join(PROJECT_ROOT, "assets/ambient/sad.mp3"),
        "anxious": os.path.join(PROJECT_ROOT, "assets/ambient/anxious.mp3"),
        "calm": os.path.join(PROJECT_ROOT, "assets/ambient/calm.mp3"),
        "happy": os.path.join(PROJECT_ROOT, "assets/ambient/happy.mp3"),
        "default": os.path.join(PROJECT_ROOT, "assets/ambient/default.mp3"),
    }

    ambient_path = ambient_map.get(mood, ambient_map["default"])

    if not os.path.exists(ambient_path):
        print("Ambient file does not exist!")
        return voice_path
    if not os.path.exists(voice_path):
        print("[Mixer] Voice file not found! Cannot mix.")
        return voice_path

    print("[Mixer] Loading voice audio...")
    voice = AudioSegment.from_file(voice_path)
    ambient = AudioSegment.from_file(ambient_path)

    if len(ambient) < len(voice):
        ambient = ambient * (len(voice) // len(ambient) + 1)

    ambient = ambient[:len(voice)]  # match audio lengths
    ambient = ambient[:len(voice)] - 18  # reduce volume
    mixed = voice.overlay(ambient)

    output_dir = os.path.join(settings.MEDIA_ROOT, "audio") 
    os.makedirs(output_dir, exist_ok=True)

    final_path = os.path.join(output_dir, f"podcast_{podcast_id}.mp3")

    mixed.export(final_path, format="mp3")
    print(f"[Mixer] Final mixed audio saved → {final_path}")
    print(f"Mixed audio saved at: {final_path}")
    return final_path
