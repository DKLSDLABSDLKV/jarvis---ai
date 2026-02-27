"""
Activity Logging Module for Secure Intelligent Desktop Assistant
Logs all activities: login attempts, commands, errors, file actions
"""

import logging
import os
from datetime import datetime
from pathlib import Path
import pickle

# Import config
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class ActivityLogger:
    """
    Centralized logging system for the assistant
    Handles all types of logging activities
    """
    
    def __init__(self, log_file=None):
        """Initialize the logger with file and console handlers"""
        self.log_file = log_file or config.LOG_FILE
        self.logger = None
        self._setup_logger()
    
    def _setup_logger(self):
        """Configure the logging system"""
        # Create logger
        self.logger = logging.getLogger('DesktopAssistant')
        self.logger.setLevel(getattr(logging, config.LOG_LEVEL))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        formatter = logging.Formatter(config.LOG_FORMAT, config.LOG_DATE_FORMAT)
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info("=" * 60)
        self.logger.info(f"{config.APP_NAME} v{config.APP_VERSION}")
        self.logger.info("Logging system initialized")
        self.logger.info("=" * 60)
    
    def info(self, message, category="INFO"):
        """Log info message"""
        self.logger.info(f"[{category}] {message}")
    
    def warning(self, message, category="WARNING"):
        """Log warning message"""
        self.logger.warning(f"[{category}] {message}")
    
    def error(self, message, category="ERROR"):
        """Log error message"""
        self.logger.error(f"[{category}] {message}")
    
    def debug(self, message, category="DEBUG"):
        """Log debug message"""
        self.logger.debug(f"[{category}] {message}")
    
    def log_login_attempt(self, success, username=None, face_id=None):
        """Log face recognition login attempt"""
        status = "SUCCESS" if success else "FAILED"
        if username:
            message = f"Login attempt - Status: {status}, User: {username}"
        elif face_id:
            message = f"Login attempt - Status: {status}, Face ID: {face_id}"
        else:
            message = f"Login attempt - Status: {status}"
        
        if success:
            self.logger.info(f"[LOGIN] {message}")
        else:
            self.logger.warning(f"[LOGIN] {message}")
    
    def log_command(self, command, intent, confidence=None):
        """Log voice command"""
        if confidence:
            message = f"Command: '{command}' | Intent: {intent} | Confidence: {confidence:.2f}"
        else:
            message = f"Command: '{command}' | Intent: {intent}"
        self.logger.info(f"[COMMAND] {message}")
    
    def log_file_operation(self, operation, file_path, success=True):
        """Log file management operation"""
        status = "SUCCESS" if success else "FAILED"
        message = f"File operation: {operation} | Path: {file_path} | Status: {status}"
        if success:
            self.logger.info(f"[FILE] {message}")
        else:
            self.logger.error(f"[FILE] {message}")
    
    def log_error(self, error, context=None):
        """Log error with context"""
        if context:
            message = f"Error in {context}: {str(error)}"
        else:
            message = f"Error: {str(error)}"
        self.logger.exception(message)
    
    def log_system_event(self, event_type, details):
        """Log system event"""
        self.logger.info(f"[SYSTEM] {event_type}: {details}")
    
    def log_reminder(self, reminder_time, message):
        """Log reminder creation"""
        self.logger.info(f"[REMINDER] Scheduled for {reminder_time}: {message}")
    
    def log_weather_request(self, location):
        """Log weather request"""
        self.logger.info(f"[WEATHER] Requested for location: {location}")
    
    def log_news_request(self, category=None):
        """Log news request"""
        category_str = f"Category: {category}" if category else "General news"
        self.logger.info(f"[NEWS] Requested - {category_str}")
    
    def log_chat_request(self, message, response=None):
        """Log AI chat interaction"""
        if response:
            self.logger.info(f"[CHAT] User: '{message}' | AI: '{response[:50]}...'")
        else:
            self.logger.info(f"[CHAT] User: '{message}'")
    
    def log_sentiment(self, text, sentiment, score):
        """Log sentiment analysis result"""
        self.logger.debug(f"[SENTIMENT] Text: '{text[:30]}...' | Sentiment: {sentiment} | Score: {score:.3f}")
    
    def log_permission_denied(self, user, permission):
        """Log permission denied event"""
        self.logger.warning(f"[PERMISSION] User: {user} | Denied: {permission}")
    
    def log_inactivity_lock(self, username):
        """Log inactivity lock event"""
        self.logger.info(f"[SECURITY] Auto-lock triggered for user: {username}")


# Global logger instance
_logger_instance = None


def setup_logger(log_file=None):
    """
    Setup and return the global logger instance
    
    Args:
        log_file: Optional custom log file path
        
    Returns:
        ActivityLogger instance
    """
    global _logger_instance
    _logger_instance = ActivityLogger(log_file)
    return _logger_instance


def get_logger():
    """
    Get the current logger instance
    
    Returns:
        ActivityLogger instance
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = setup_logger()
    return _logger_instance


# Convenience functions
def log_activity(message, category="INFO"):
    """Log an activity message"""
    get_logger().info(message, category)


def log_error(error, context=None):
    """Log an error"""
    get_logger().log_error(error, context)


def log_command(command, intent, confidence=None):
    """Log a voice command"""
    get_logger().log_command(command, intent, confidence)


# ============================================
# Log File Management
# ============================================

def rotate_logs(max_size_mb=10, backup_count=5):
    """
    Rotate log files when they exceed max size
    
    Args:
        max_size_mb: Maximum size in MB before rotation
        backup_count: Number of backup files to keep
    """
    import shutil
    from pathlib import Path
    
    log_file = Path(config.LOG_FILE)
    if not log_file.exists():
        return
    
    size_mb = log_file.stat().st_size / (1024 * 1024)
    
    if size_mb > max_size_mb:
        # Rotate existing backups
        for i in range(backup_count - 1, 0, -1):
            src = log_file.with_suffix(f'.log.{i}')
            dst = log_file.with_suffix(f'.log.{i + 1}')
            if dst.exists():
                dst.unlink()
            if src.exists():
                shutil.move(str(src), str(dst))
        
        # Move current log to backup
        backup = log_file.with_suffix('.log.1')
        shutil.move(str(log_file), str(backup))
        
        # Create new log file
        setup_logger()


def get_recent_logs(lines=100):
    """
    Get recent log entries
    
    Args:
        lines: Number of lines to retrieve
        
    Returns:
        List of log lines
    """
    try:
        with open(config.LOG_FILE, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return all_lines[-lines:]
    except FileNotFoundError:
        return []


def search_logs(pattern):
    """
    Search logs for a pattern
    
    Args:
        pattern: Regex pattern to search
        
    Returns:
        List of matching lines
    """
    import re
    matches = []
    try:
        with open(config.LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if re.search(pattern, line, re.IGNORECASE):
                    matches.append(line.strip())
    except FileNotFoundError:
        pass
    return matches
