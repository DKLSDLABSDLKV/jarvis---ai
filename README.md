# Secure Intelligent Desktop Assistant with Face Recognition and NLP

A production-ready voice-controlled desktop assistant built with Python, featuring face recognition authentication, ML-based intent classification, and natural language processing.

## Features

### 🔐 Security
- Face Recognition Login (webcam authentication)
- Role-based permission system
- Data encryption for stored information
- Session management with inactivity auto-lock

### 🎙️ Voice Control
- Wake word activation ("Hey Aditya")
- Speech-to-text recognition (online/offline)
- Text-to-speech responses
- Task confirmation system for risky actions

### 🤖 AI & ML
- Intent Classification using TF-IDF + ML (Logistic Regression/Random Forest)
- Sentiment Analysis (positive/negative/neutral detection)
- Offline NLP using spaCy
- OpenAI GPT integration for chat

### 📊 System Monitoring
- Real-time CPU, RAM, Disk usage
- Battery status monitoring
- System health reports

### 📁 File Management
- Create, delete, search files
- Voice-guided file operations
- Operation logging

### ⏰ Reminders
- Schedule reminders via voice
- Voice notifications
- Persistent storage

### 🌦️ External APIs
- Weather updates (OpenWeather API)
- News headlines (News API)

## Project Structure

```
AI/
├── main.py                 # Main application entry point
├── config.py               # Centralized configuration
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── core/
│   ├── voice.py            # Voice recognition & TTS
│   ├── face_auth.py        # Face recognition
│   └── nlp_processor.py    # NLP processing
├── ml/
│   ├── intent_model.py     # Intent classification
│   └── sentiment.py        # Sentiment analysis
├── features/
│   ├── system_monitor.py   # System monitoring
│   ├── file_manager.py     # File operations
│   ├── reminder.py         # Reminders
│   ├── weather.py          # Weather service
│   ├── news.py             # News service
│   └── chat_module.py     # AI chat
├── security/
│   ├── permissions.py      # Role-based access
│   └── encryption.py      # Data encryption
├── logs/                   # Logging module
├── models/                 # Trained ML models
├── data/
│   ├── intents.json       # Intent training data
│   └── authorized_faces/  # Face encodings
└── tests/                  # Test files
```

## Installation

### 1. Install Python Dependencies
```
bash
pip install -r requirements.txt
```

### 2. Download Required Models
```
bash
# Download spaCy English model
python -m spacy download en_core_web_sm

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon'); nltk.download('wordnet')"
```

### 3. Configure API Keys
Create a `.env` file or set environment variables:
```
OPENWEATHER_API_KEY=your_api_key_here
NEWS_API_KEY=your_api_key_here
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Running the Assistant
```
bash
python main.py
```

### Initial Setup
1. On first run, the assistant will prompt to enroll your face
2. Say "Enroll my face" to add your face to authorized users
3. Say "Hey Aditya" to activate the assistant
4. Follow up with your command

### Example Commands
- "Hey Aditya, what's the weather?"
- "Hey Aditya, open Chrome"
- "Hey Aditya, check system status"
- "Hey Aditya, remind me to call John in 30 minutes"
- "Hey Aditya, what's the latest news?"
- "Hey Aditya, create a new file called notes"

## Configuration

Edit `config.py` to customize:
- Wake word
- Voice settings (rate, volume)
- ML model parameters
- API keys
- Security settings

## Troubleshooting

### Microphone not detected
- Check microphone permissions
- Install portaudio: `pip install pyaudio`

### Face recognition not working
- Ensure webcam is connected
- Install dlib properly (requires CMake)

### Module import errors
- Ensure all dependencies are installed
- Check Python version (3.8+ recommended)

## License

MIT License

## Author

Created by AI Assistant
