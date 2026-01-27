import uuid
import os
from pydub import AudioSegment
from django.conf import settings


def mix_voice_with_ambient(voice_path, mood, podcast_id):
    print(f"Mixing ambient sound for mood: {mood}")
    mood = mood.lower()
    PROJECT_ROOT = os.path.dirname(settings.BASE_DIR)
    ambient_map = {
        "peaceful": os.path.join(PROJECT_ROOT, "assets/ambient/peaceful.mp3"),
        "sad": os.path.join(PROJECT_ROOT, "assets/ambient/sad.mp3"),
        "anxious": os.path.join(PROJECT_ROOT, "assets/ambient/anxious.mp3"),
        "tired": os.path.join(PROJECT_ROOT, "assets/ambient/tired.mp3"),
        "thoughtful": os.path.join(PROJECT_ROOT, "assets/ambient/thoughtful.mp3"),
        "default": os.path.join(PROJECT_ROOT, "assets/ambient/default.mp3"),
    }

    ambient_path = ambient_map.get(mood, ambient_map["default"])
    if not os.path.exists(ambient_path):
        print("Ambient file does not exist!")
        return voice_path

    voice = AudioSegment.from_file(voice_path)
    ambient = AudioSegment.from_file(ambient_path)

    if len(ambient) < len(voice):
        ambient = ambient * (len(voice) // len(ambient) + 1)
    
    ambient = ambient[:len(voice)] - 10  # reduce volume
    mixed = voice.overlay(ambient)

    output_dir = os.path.join(settings.MEDIA_ROOT, "audio")
    os.makedirs(output_dir, exist_ok=True)

    # Generate a short unique ID string
    unique_id = uuid.uuid4().hex[:8]

    # Use the unique ID in the filename
    #final_path = os.path.join(output_dir, f"final_mix_{mood}_{unique_id}.mp3")

    final_path = os.path.join(output_dir, f"podcast_{podcast_id}.mp3")

    mixed.export(final_path, format="mp3")
    print(f"Mixed audio saved at: {final_path}")
    return final_path
