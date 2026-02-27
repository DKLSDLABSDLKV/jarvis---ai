"""
Centralized Configuration for Secure Intelligent Desktop Assistant
Contains all settings, API keys, and paths configuration
"""

import os
from pathlib import Path

# ============================================
# PROJECT PATHS
# ============================================
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"
AUTHORIZED_FACES_DIR = DATA_DIR / "authorized_faces"

# Create directories if they don't exist
LOGS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
AUTHORIZED_FACES_DIR.mkdir(exist_ok=True)

# ============================================
# FILE PATHS
# ============================================
LOG_FILE = LOGS_DIR / "assistant.log"
INTENTS_FILE = DATA_DIR / "intents.json"
REMINDERS_FILE = DATA_DIR / "reminders.json"
TRAINED_MODEL_PATH = MODELS_DIR / "intent_classifier.pkl"
VECTORIZER_PATH = MODELS_DIR / "tfidf_vectorizer.pkl"
ENCODINGS_FILE = DATA_DIR / "face_encodings.pkl"

# ============================================
# FACE RECOGNITION CONFIG
# ============================================
FACE_TOLERANCE = 0.6  # Lower = more strict
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
WAKE_WORD = "hey aditya"

# ============================================
# VOICE CONFIG
# ============================================
LANGUAGE = "en-US"
VOICE_RATE = 150  # Words per minute
VOICE_VOLUME = 0.9
VOICE_NAME = None  # Use default

# ============================================
# ML MODEL CONFIG
# ============================================
INTENT_CONFIDENCE_THRESHOLD = 0.7
USE_RANDOM_FOREST = True  # Alternative: Logistic Regression
MAX_FEATURES = 1000
N_GRAMS = (1, 2)

# ============================================
# API CONFIG (Placeholders - User must fill)
# ============================================
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "YOUR_API_KEY_HERE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_API_KEY_HERE")

# ============================================
# SYSTEM MONITORING CONFIG
# ============================================
CPU_WARNING_THRESHOLD = 80  # Percentage
RAM_WARNING_THRESHOLD = 80  # Percentage
DISK_WARNING_THRESHOLD = 90  # Percentage
BATTERY_WARNING_THRESHOLD = 20  # Percentage

# ============================================
# SECURITY CONFIG
# ============================================
INACTIVITY_LOCK_TIMEOUT = 300  # seconds (5 minutes)
ENABLE_ENCRYPTION = True
SESSION_TIMEOUT = 1800  # 30 minutes

# ============================================
# SENTIMENT THRESHOLDS
# ============================================
POSITIVE_THRESHOLD = 0.1
NEGATIVE_THRESHOLD = -0.1

# ============================================
# USER ROLES
# ============================================
class UserRole:
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

# ============================================
# PERMISSION LEVELS
# ============================================
class Permission:
    FACE_LOGIN = "face_login"
    VOICE_CONTROL = "voice_control"
    FILE_MANAGEMENT = "file_management"
    SYSTEM_MONITOR = "system_monitor"
    WEATHER_ACCESS = "weather_access"
    NEWS_ACCESS = "news_access"
    AI_CHAT = "ai_chat"
    REMINDER_SET = "reminder_set"
    EMAIL_SEND = "email_send"

# Role-based permissions
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        Permission.FACE_LOGIN,
        Permission.VOICE_CONTROL,
        Permission.FILE_MANAGEMENT,
        Permission.SYSTEM_MONITOR,
        Permission.WEATHER_ACCESS,
        Permission.NEWS_ACCESS,
        Permission.AI_CHAT,
        Permission.REMINDER_SET,
        Permission.EMAIL_SEND,
    ],
    UserRole.USER: [
        Permission.FACE_LOGIN,
        Permission.VOICE_CONTROL,
        Permission.FILE_MANAGEMENT,
        Permission.SYSTEM_MONITOR,
        Permission.WEATHER_ACCESS,
        Permission.NEWS_ACCESS,
        Permission.AI_CHAT,
        Permission.REMINDER_SET,
    ],
    UserRole.GUEST: [
        Permission.FACE_LOGIN,
        Permission.VOICE_CONTROL,
        Permission.SYSTEM_MONITOR,
        Permission.WEATHER_ACCESS,
        Permission.NEWS_ACCESS,
    ],
}

# ============================================
# LOGGING CONFIG
# ============================================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============================================
# APPLICATION CONFIG
# ============================================
APP_NAME = "Secure Intelligent Desktop Assistant"
APP_VERSION = "1.0.0"
DEBUG_MODE = False
