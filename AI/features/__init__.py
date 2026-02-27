"""Features package for Secure Intelligent Desktop Assistant"""
from .system_monitor import SystemMonitor
from .file_manager import FileManager
from .reminder import ReminderManager
from .weather import WeatherService
from .news import NewsService
from .chat_module import ChatModule

__all__ = [
    'SystemMonitor', 
    'FileManager', 
    'ReminderManager', 
    'WeatherService', 
    'NewsService', 
    'ChatModule'
]
