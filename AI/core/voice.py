"""
Voice Engine Module for Secure Intelligent Desktop Assistant
Handles speech recognition (STT) and text-to-speech (TTS)
"""

import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
import logging
from pathlib import Path
import sys

# Import config
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class VoiceEngine:
    """
    Voice Engine for Speech Recognition and Text-to-Speech
    Supports wake word detection, offline mode, and multiple voices
    """
    
    def __init__(self):
        """Initialize the voice engine"""
        self.logger = logging.getLogger('DesktopAssistant.Voice')
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.tts_engine = None
        self.is_listening = False
        self.wake_word = config.WAKE_WORD.lower()
        self.language = config.LANGUAGE
        self.command_queue = queue.Queue()
        self.is_speaking = False
        self.speech_thread = None
        
        # Initialize components
        self._init_microphone()
        self._init_tts()
        
        self.logger.info("Voice Engine initialized successfully")
    
    def _init_microphone(self):
        """Initialize the microphone"""
        try:
            self.microphone = sr.Microphone()
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.logger.info("Microphone initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize microphone: {e}")
            self.microphone = None
    
    def _init_tts(self):
        """Initialize text-to-speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Set properties
            self.tts_engine.setProperty('rate', config.VOICE_RATE)
            self.tts_engine.setProperty('volume', config.VOICE_VOLUME)
            
            # Try to set voice
            if config.VOICE_NAME:
                voices = self.tts_engine.getProperty('voices')
                for voice in voices:
                    if config.VOICE_NAME.lower() in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            self.logger.info("TTS engine initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS engine: {e}")
            self.tts_engine = None
    
    def speak(self, text, async_mode=True):
        """
        Convert text to speech
        
        Args:
            text: Text to speak
            async_mode: If True, speak in background thread
        """
        if not self.tts_engine:
            self.logger.warning("TTS engine not available, skipping speech")
            return
        
        def _speak():
            try:
                self.is_speaking = True
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                self.logger.error(f"Error during speech: {e}")
            finally:
                self.is_speaking = False
        
        if async_mode:
            thread = threading.Thread(target=_speak, daemon=True)
            thread.start()
        else:
            _speak()
    
    def speak_and_wait(self, text):
        """Speak text and wait for completion"""
        self.speak(text, async_mode=False)
    
    def listen_for_wake_word(self, timeout=10):
        """
        Listen for wake word
        
        Args:
            timeout: Maximum seconds to wait for wake word
            
        Returns:
            True if wake word detected, False otherwise
        """
        if not self.microphone:
            self.logger.error("Microphone not available")
            return False
        
        self.logger.info(f"Listening for wake word: '{self.wake_word}'")
        
        try:
            with self.microphone as source:
                # Listen for wake word
                audio = self.recognizer.listen(source, timeout=timeout)
            
            # Recognize speech
            try:
                text = self.recognizer.recognize_google(audio).lower()
                self.logger.debug(f" Heard: '{text}'")
                
                if self.wake_word in text:
                    self.logger.info("Wake word detected!")
                    # Acknowledge wake word
                    self.speak("I'm listening")
                    return True
            except sr.UnknownValueError:
                self.logger.debug("Could not understand audio")
            except sr.RequestError as e:
                self.logger.error(f"Speech recognition service error: {e}")
        
        except sr.WaitTimeoutError:
            self.logger.debug("Wake word listening timed out")
        except Exception as e:
            self.logger.error(f"Error in wake word detection: {e}")
        
        return False
    
    def listen_for_command(self, timeout=10, phrase_time_limit=15):
        """
        Listen for a voice command
        
        Args:
            timeout: Max seconds to wait for speech to start
            phrase_time_limit: Max seconds to record
            
        Returns:
            Recognized command text or None
        """
        if not self.microphone:
            self.logger.error("Microphone not available")
            return None
        
        try:
            with self.microphone as source:
                self.logger.debug("Listening for command...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            # Try online recognition first
            try:
                text = self.recognizer.recognize_google(audio, language=self.language)
                self.logger.info(f"Recognized command: '{text}'")
                return text
            except sr.UnknownValueError:
                self.logger.warning("Could not understand audio")
                self.speak("Sorry, I didn't catch that. Could you please repeat?")
            except sr.RequestError:
                # Fall back to offline mode
                self.logger.warning("Online recognition failed, trying offline")
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    self.logger.info(f"Recognized command (offline): '{text}'")
                    return text
                except sr.UnknownValueError:
                    self.logger.warning("Offline recognition failed")
                except sr.RequestError as e:
                    self.logger.error(f"Offline recognition error: {e}")
        
        except sr.WaitTimeoutError:
            self.logger.debug("Command listening timed out")
        except Exception as e:
            self.logger.error(f"Error listening for command: {e}")
        
        return None
    
    def confirm_action(self, action_description):
        """
        Ask user to confirm a risky action
        
        Args:
            action_description: Description of the action to confirm
            
        Returns:
            True if confirmed, False otherwise
        """
        confirmation_text = f"Are you sure you want to {action_description}? Please say yes or no."
        self.speak(confirmation_text)
        
        # Listen for confirmation
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            response = self.listen_for_command(timeout=5)
            
            if response:
                response_lower = response.lower()
                
                # Check for positive confirmation
                if any(word in response_lower for word in ['yes', 'yeah', 'sure', 'ok', 'okay', 'confirm', 'go ahead', 'do it']):
                    self.speak("Confirmed. Proceeding with the action.")
                    return True
                
                # Check for negative confirmation
                elif any(word in response_lower for word in ['no', 'nope', 'cancel', 'stop', 'wait', 'don\'t']):
                    self.speak("Action cancelled.")
                    return False
                
                # Unclear response
                else:
                    self.speak("I didn't catch that. Please say yes or no.")
                    attempts += 1
            else:
                attempts += 1
        
        self.speak("No confirmation received. Action cancelled.")
        return False
    
    def listen_continuously(self, callback=None):
        """
        Continuously listen for commands after wake word
        
        Args:
            callback: Function to call with recognized commands
            
        Returns:
            None (runs in infinite loop)
        """
        self.is_listening = True
        self.logger.info("Started continuous listening mode")
        
        while self.is_listening:
            # Wait for wake word
            if self.listen_for_wake_word(timeout=15):
                # Then listen for command
                command = self.listen_for_command(timeout=10)
                
                if command and callback:
                    callback(command)
        
        self.logger.info("Stopped continuous listening mode")
    
    def stop_listening(self):
        """Stop continuous listening"""
        self.is_listening = False
    
    def get_available_voices(self):
        """Get list of available TTS voices"""
        if not self.tts_engine:
            return []
        
        voices = self.tts_engine.getProperty('voices')
        return [(voice.id, voice.name) for voice in voices]
    
    def set_voice(self, voice_id):
        """Set the TTS voice"""
        if self.tts_engine:
            self.tts_engine.setProperty('voice', voice_id)
    
    def set_rate(self, rate):
        """Set speech rate"""
        if self.tts_engine:
            self.tts_engine.setProperty('rate', rate)
    
    def set_volume(self, volume):
        """Set speech volume (0.0 to 1.0)"""
        if self.tts_engine:
            self.tts_engine.setProperty('volume', volume)
    
    def cleanup(self):
        """Clean up resources"""
        self.is_listening = False
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
        self.logger.info("Voice engine cleaned up")


# ============================================
# Offline Voice Recognition
# ============================================

class OfflineVoiceEngine:
    """
    Offline voice recognition using CMU Sphinx
    Fallback when internet is not available
    """
    
    def __init__(self):
        """Initialize offline voice engine"""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.logger = logging.getLogger('DesktopAssistant.OfflineVoice')
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
    
    def listen(self, timeout=10, phrase_time_limit=15):
        """
        Listen for speech (offline)
        
        Args:
            timeout: Max seconds to wait for speech
            phrase_time_limit: Max seconds to record
            
        Returns:
            Recognized text or None
        """
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            # Use Sphinx for offline recognition
            text = self.recognizer.recognize_sphinx(audio)
            self.logger.info(f"Offline recognition: '{text}'")
            return text
        
        except sr.UnknownValueError:
            self.logger.warning("Could not understand audio")
        except sr.RequestError as e:
            self.logger.error(f"Sphinx recognition error: {e}")
        except Exception as e:
            self.logger.error(f"Error in offline recognition: {e}")
        
        return None


# ============================================
# Main function for testing
# ============================================

def test_voice_engine():
    """Test the voice engine"""
    print("Testing Voice Engine...")
    
    engine = VoiceEngine()
    
    # Test TTS
    print("\nTesting TTS...")
    engine.speak("Hello! I am your desktop assistant.")
    
    # Get available voices
    print("\nAvailable voices:")
    for voice_id, voice_name in engine.get_available_voices():
        print(f"  - {voice_name}")
    
    print("\nVoice engine test complete!")
    return engine


if __name__ == "__main__":
    test_voice_engine()
