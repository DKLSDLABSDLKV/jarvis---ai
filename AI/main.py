"""
Secure Intelligent Desktop Assistant
Main Application - Voice-Controlled Desktop Assistant with Face Recognition and NLP

Author: AI Assistant
Version: 1.0.0
"""

import sys
import logging
import threading
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import configuration
import config

# Import core modules
from core.voice import VoiceEngine
from core.face_auth import FaceAuthenticator
from core.nlp_processor import NLPProcessor

# Import ML modules
from ml.intent_model import IntentClassifier
from ml.sentiment import SentimentAnalyzer

# Import feature modules
from features.system_monitor import SystemMonitor
from features.file_manager import FileManager
from features.reminder import ReminderManager
from features.weather import WeatherService
from features.news import NewsService
from features.chat_module import ChatModule

# Import security modules
from security.permissions import PermissionManager
from security.encryption import DataEncryptor

# Import logging
from logs.logger import setup_logger, get_logger


class DesktopAssistant:
    """
    Main Desktop Assistant Class
    Integrates all modules and handles voice commands
    """
    
    def __init__(self):
        """Initialize the desktop assistant"""
        # Setup logging
        self.logger = setup_logger()
        self.logger.info("Initializing Desktop Assistant...")
        
        # Initialize state
        self.is_authenticated = False
        self.current_user = None
        self.session_id = None
        self.is_running = False
        
        # Initialize all modules
        self._initialize_modules()
        
        self.logger.info("Desktop Assistant initialized successfully")
    
    def _initialize_modules(self):
        """Initialize all assistant modules"""
        try:
            # Core modules
            self.logger.info("Initializing core modules...")
            self.voice_engine = VoiceEngine()
            self.face_auth = FaceAuthenticator()
            self.nlp_processor = NLPProcessor()
            
            # ML modules
            self.logger.info("Initializing ML modules...")
            self.intent_classifier = IntentClassifier()
            self.sentiment_analyzer = SentimentAnalyzer()
            
            # Feature modules
            self.logger.info("Initializing feature modules...")
            self.system_monitor = SystemMonitor()
            self.file_manager = FileManager()
            self.reminder_manager = ReminderManager()
            self.weather_service = WeatherService()
            self.news_service = NewsService()
            self.chat_module = ChatModule()
            
            # Security modules
            self.logger.info("Initializing security modules...")
            self.permission_manager = PermissionManager()
            self.encryptor = DataEncryptor()
            
            self.logger.info("All modules initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing modules: {e}")
            raise
    
    def authenticate(self):
        """Authenticate user using face recognition"""
        self.logger.info("Starting authentication...")
        
        # Try face authentication
        success, username = self.face_auth.authenticate(max_attempts=3)
        
        if success:
            self.is_authenticated = True
            self.current_user = username
            
            # Create session
            self.session_id = self.permission_manager.create_session(username)
            
            # Set user role (default to user)
            self.permission_manager.set_user_role(username, config.UserRole.USER)
            
            self.logger.info(f"User {username} authenticated successfully")
            return True
        else:
            self.logger.warning("Authentication failed")
            return False
    
    def process_command(self, command):
        """
        Process voice command
        
        Args:
            command: Voice command string
            
        Returns:
            Response string
        """
        self.logger.info(f"Processing command: {command}")
        
        # Analyze sentiment
        sentiment_result = self.sentiment_analyzer.analyze(command)
        self.logger.debug(f"Sentiment: {sentiment_result['sentiment']}")
        
        # Get intent prediction
        intent_result = self.intent_classifier.predict_with_confidence(command)
        intent = intent_result['intent']
        confidence = intent_result['confidence']
        
        self.logger.info(f"Intent: {intent}, Confidence: {confidence:.2f}")
        
        # Log command
        get_logger().log_command(command, intent, confidence)
        
        # Process based on intent
        response = self._execute_intent(intent, command, confidence)
        
        # Adjust response for sentiment
        response = self.sentiment_analyzer.adjust_response_for_sentiment(
            response, sentiment_result
        )
        
        return response
    
    def _execute_intent(self, intent, command, confidence):
        """Execute the recognized intent"""
        
        if intent is None or confidence < config.INTENT_CONFIDENCE_THRESHOLD:
            # Low confidence - use chat module
            return self.chat_module.chat(command)
        
        # Process based on intent
        intent_handlers = {
            'open_app': self._handle_open_app,
            'system_status': self._handle_system_status,
            'weather': self._handle_weather,
            'news': self._handle_news,
            'reminder': self._handle_reminder,
            'chat': self._handle_chat,
            'create_file': self._handle_create_file,
            'delete_file': self._handle_delete_file,
            'search_file': self._handle_search_file,
            'send_email': self._handle_send_email,
            'shutdown': self._handle_shutdown,
            'help': self._handle_help,
        }
        
        handler = intent_handlers.get(intent)
        if handler:
            return handler(command)
        else:
            return f"I understood you want to {intent}, but I'm not sure how to help with that."
    
    def _handle_open_app(self, command):
        """Handle open app intent"""
        # Extract app name from command
        nlp_result = self.nlp_processor.simple_parse(command)
        
        # Map common app names
        app_mapping = {
            'chrome': 'chrome',
            'notepad': 'notepad',
            'calculator': 'calculator',
            'browser': 'chrome',
            'word': 'winword',
            'excel': 'excel',
            'spotify': 'spotify',
        }
        
        # Try to find app name in command
        for key, value in app_mapping.items():
            if key in command.lower():
                # Open the application (using subprocess)
                try:
                    import subprocess
                    subprocess.Popen(value)
                    return f"Opening {key}..."
                except Exception as e:
                    return f"Sorry, I couldn't open {key}. Error: {str(e)}"
        
        return "Which application would you like me to open?"
    
    def _handle_system_status(self, command):
        """Handle system status intent"""
        report = self.system_monitor.speak_health_report(self.voice_engine)
        return report
    
    def _handle_weather(self, command):
        """Handle weather intent"""
        # Extract location from command
        nlp_result = self.nlp_processor.simple_parse(command)
        locations = nlp_result.get('location', [])
        
        if locations:
            city = locations[0]
        else:
            # Default city
            city = "London"
        
        report = self.weather_service.speak_weather(city, self.voice_engine)
        return report
    
    def _handle_news(self, command):
        """Handle news intent"""
        report = self.news_service.speak_headlines(
            voice_engine=self.voice_engine,
            max_headlines=3
        )
        return report
    
    def _handle_reminder(self, command):
        """Handle reminder intent"""
        # Extract time and message
        nlp_result = self.nlp_processor.simple_parse(command)
        time_info = nlp_result.get('time', {})
        
        # Parse reminder details
        message = command.lower().replace('remind me', '').replace('reminder', '').strip()
        message = message.replace('to', '', 1).strip()
        
        # Set reminder
        if 'minutes' in time_info:
            minutes = time_info['minutes']
            self.reminder_manager.set_reminder(message, minutes=minutes)
            return f"I'll remind you in {minutes} minutes: {message}"
        elif 'hours' in time_info:
            hours = time_info['hours']
            self.reminder_manager.set_reminder(message, hours=hours)
            return f"I'll remind you in {hours} hours: {message}"
        else:
            # Default to 1 hour
            self.reminder_manager.set_reminder(message, hours=1)
            return f"I'll remind you in 1 hour: {message}"
    
    def _handle_chat(self, command):
        """Handle chat intent"""
        response = self.chat_module.speak_response(command, self.voice_engine)
        return response
    
    def _handle_create_file(self, command):
        """Handle create file intent"""
        self.voice_engine.speak("What would you like to name the file?")
        filename = self.voice_engine.listen_for_command(timeout=10)
        
        if filename:
            # Get user's documents folder
            import os
            docs_path = str(Path.home() / "Documents")
            file_path = f"{docs_path}/{filename}"
            
            if self.file_manager.create_file(file_path, ""):
                return f"Created file: {filename}"
            else:
                return f"Sorry, I couldn't create the file."
        
        return "File creation cancelled."
    
    def _handle_delete_file(self, command):
        """Handle delete file intent"""
        # Ask for confirmation
        if self.voice_engine.confirm_action("delete the file"):
            # Extract filename from command
            nlp_result = self.nlp_processor.simple_parse(command)
            nouns = nlp_result.get('entities', [])
            
            if nouns:
                filename = nouns[0]
                import os
                file_path = str(Path.home() / "Documents" / filename)
                
                if self.file_manager.delete_file(file_path):
                    return f"Deleted file: {filename}"
                else:
                    return f"Sorry, I couldn't delete the file."
        
        return "File deletion cancelled."
    
    def _handle_search_file(self, command):
        """Handle search file intent"""
        # Extract search term
        search_term = command.lower()
        search_term = search_term.replace('search', '').replace('find', '').strip()
        
        if search_term:
            import os
            home_dir = str(Path.home())
            results = self.file_manager.search_files(home_dir, f"*{search_term}*")
            
            if results:
                return f"Found {len(results)} files: {', '.join(results[:5])}"
            else:
                return f"No files found matching: {search_term}"
        
        return "What would you like me to search for?"
    
    def _handle_send_email(self, command):
        """Handle send email intent"""
        return "Email functionality requires additional setup. Please configure SMTP settings."
    
    def _handle_shutdown(self, command):
        """Handle shutdown intent"""
        if self.voice_engine.confirm_action("shutdown the computer"):
            return "Shutting down the system..."
        return "Shutdown cancelled."
    
    def _handle_help(self, command):
        """Handle help intent"""
        help_text = """
        I can help you with the following:
        - Opening applications (Chrome, Notepad, Calculator, etc.)
        - Checking system status (CPU, RAM, Disk usage)
        - Getting weather updates
        - Reading latest news
        - Setting reminders
        - Creating and managing files
        - Searching for files
        - Having a conversation
        - And much more!
        
        Just say "Hey Aditya" followed by your command.
        """
        self.voice_engine.speak(help_text)
        return help_text
    
    def start(self):
        """Start the desktop assistant"""
        self.logger.info("Starting Desktop Assistant...")
        self.is_running = True
        
        # Start reminder scheduler
        self.reminder_manager.set_voice_engine(self.voice_engine)
        self.reminder_manager.start_scheduler()
        
        # Main loop
        self._main_loop()
    
    def _main_loop(self):
        """Main interaction loop"""
        self.logger.info("Entering main loop...")
        
        while self.is_running:
            try:
                # Wait for wake word
                if self.voice_engine.listen_for_wake_word(timeout=15):
                    # Listen for command
                    command = self.voice_engine.listen_for_command(timeout=10)
                    
                    if command:
                        # Process command
                        response = self.process_command(command)
                        
                        # Speak response
                        self.voice_engine.speak(response)
            
            except KeyboardInterrupt:
                self.logger.info("Received keyboard interrupt")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(1)
        
        self.stop()
    
    def stop(self):
        """Stop the desktop assistant"""
        self.logger.info("Stopping Desktop Assistant...")
        self.is_running = False
        
        # Stop reminder scheduler
        self.reminder_manager.stop_scheduler()
        
        # End session
        if self.session_id:
            self.permission_manager.end_session(self.session_id)
        
        # Cleanup voice engine
        self.voice_engine.cleanup()
        
        self.logger.info("Desktop Assistant stopped")


def main():
    """Main entry point"""
    print("="*60)
    print(f" {config.APP_NAME} v{config.APP_VERSION}")
    print("="*60)
    print("\nInitializing...")
    
    try:
        # Create assistant
        assistant = DesktopAssistant()
        
        # Authenticate
        print("\nAuthentication required. Please look at the camera...")
        
        if assistant.authenticate():
            print("\nAuthentication successful! Starting assistant...")
            
            # Start assistant
            assistant.start()
        else:
            print("\nAuthentication failed. Exiting...")
            return 1
    
    except Exception as e:
        print(f"\nError: {e}")
        logging.exception("Fatal error")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
