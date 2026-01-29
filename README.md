 MoodMate – A Calm, Ethical AI Companion for Reflection

MoodMate is a  AI-powered emotional well-being platform designed to help users pause, reflect, and build emotional awareness through journaling, audio reflection, and calming tools.  
It is intentionally non-clinical and user-controlled — focused on awareness, not diagnosis.

---

## 🧠 Key Features

- 📝 **Private Journaling**  
  Users freely write personal reflections in a secure, timestamped journal.

- 🤖 **AI Emotional Tone Analysis**  
  Analyzes language tone (e.g., calm, stress, sadness) to generate neutral, non-judgmental reflections.  
  *No diagnosis. No emotional validation.*

- 🎧 **Journal-to-Audio (Podcast)**  
  Converts journal entries into short audio reflections using AI text-to-speech with calm ambient sound.

- 🌬️ **Breathing & Grounding Exercises**  
  Simple, guided breathing tools designed for short, everyday use.

- 📚 **Blogs & Educational Content**  
  Admin-curated and user-written blogs focused on mindfulness and emotional awareness, with anonymous posting support.

---

## 🏗️ Architecture & Technology Stack

| Component              | Tools Used                                  |
|------------------------|----------------------------------------------|
| **Backend**            | Django                                       |
| **Authentication**     | Django AllAuth, OTP, JWT                     |
| **AI Processing**      |  Ollama(gemma3:4b)                                            |
| **Audio Generation**   | EDGE TTS ,Pydub
| **Media Handling**     | Pillow (secure image processing)             |
| **Database**           | SQLite (development)                         |
| **Frontend**           | Django Templates, HTML, CSS, JavaScript      |

---

## 🔄 User Flow

1. **User writes** a journal entry and optionally selects a mood.  
2. **AI analyzes** emotional tone in the text (language only).  
3. **Neutral reflection** is generated for awareness.  
4. **Optional audio podcast** is created with calm background sound.  
5. **User explores** breathing tools or educational blogs.  
6. **All data remains  user-controlled.**

---

## 🛡️ Ethics by Design

- Non-clinical, non-therapeutic system  
- No diagnosis, advice, or emotional validation  
- Full user autonomy and opt-in features  
- Privacy-first architecture with no data sharing  

---

### ⭐ Final Note

**MoodMate is not an AI therapist.**  
It is a calm, ethical companion designed to help users notice, reflect, and slow down — safely and respectfully.
