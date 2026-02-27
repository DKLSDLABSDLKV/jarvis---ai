"""
Chat Module for Secure Intelligent Desktop Assistant
AI Chat integration with OpenAI GPT
"""

import requests
import logging
import json
from pathlib import Path
import sys

# Import config
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class ChatModule:
    """
    AI Chat Module
    Handles conversation with OpenAI GPT
    """
    
    def __init__(self, api_key=None):
        """
        Initialize chat module
        
        Args:
            api_key: OpenAI API key
        """
        self.logger = logging.getLogger('DesktopAssistant.Chat')
        self.api_key = api_key or config.OPENAI_API_KEY
        self.conversation_history = []
        self.max_history = 10
        self.default_model = "gpt-3.5-turbo"
        
        if self.api_key == "YOUR_API_KEY_HERE":
            self.logger.warning("OpenAI API key not configured")
        
        self.logger.info("Chat Module initialized")
    
    def add_to_history(self, role, content):
        """
        Add message to conversation history
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
        """
        self.conversation_history.append({
            'role': role,
            'content': content
        })
        
        # Keep history limited
        if len(self.conversation_history) > self.max_history * 2:
            # Keep first message (system) and last messages
            self.conversation_history = [
                self.conversation_history[0]
            ] + self.conversation_history[-(self.max_history * 2):]
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.logger.info("Conversation history cleared")
    
    def set_system_prompt(self, prompt):
        """
        Set system prompt
        
        Args:
            prompt: System prompt text
        """
        if self.conversation_history and self.conversation_history[0]['role'] == 'system':
            self.conversation_history[0]['content'] = prompt
        else:
            self.conversation_history.insert(0, {
                'role': 'system',
                'content': prompt
            })
    
    def chat(self, message, model=None):
        """
        Send chat message to AI
        
        Args:
            message: User message
            model: Optional model override
            
        Returns:
            AI response string
        """
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            return self._fallback_response(message)
        
        # Add user message to history
        self.add_to_history('user', message)
        
        try:
            # Prepare API request
            url = "https://api.openai.com/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model or self.default_model,
                "messages": self.conversation_history,
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_message = result['choices'][0]['message']['content']
                
                # Add assistant response to history
                self.add_to_history('assistant', ai_message)
                
                self.logger.info(f"Chat response received: {ai_message[:50]}...")
                return ai_message
            
            elif response.status_code == 401:
                self.logger.error("Invalid API key")
                return "Sorry, my API key is not properly configured. Please check the settings."
            
            else:
                self.logger.error(f"API error: {response.status_code}")
                return self._fallback_response(message)
        
        except requests.exceptions.Timeout:
            self.logger.error("API request timed out")
            return "Sorry, the request timed out. Please try again."
        
        except Exception as e:
            self.logger.error(f"Chat error: {e}")
            return self._fallback_response(message)
    
    def _fallback_response(self, message):
        """
        Generate fallback response when API is not available
        
        Args:
            message: User message
            
        Returns:
            Fallback response
        """
        # Simple rule-based responses
        message_lower = message.lower()
        
        # Greetings
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return "Hello! I'm your desktop assistant. How can I help you today?"
        
        # How are you
        if 'how are you' in message_lower:
            return "I'm doing great, thank you for asking! I'm here to help you with various tasks. What would you like me to do?"
        
        # Capabilities
        if any(word in message_lower for word in ['what can you do', 'help me', 'capabilities']):
            return """I can help you with many tasks including:
- Opening applications
- Checking system status
- Getting weather and news
- Setting reminders
- Managing files
- And general conversation!
Just tell me what you need."""
        
        # Thank you
        if any(word in message_lower for word in ['thank', 'thanks']):
            return "You're welcome! Is there anything else I can help you with?"
        
        # Goodbye
        if any(word in message_lower for word in ['bye', 'goodbye', 'see you']):
            return "Goodbye! Feel free to call me whenever you need help. Have a great day!"
        
        # Default
        return "I understand you said: " + message + ". I'm configured for AI chat but need an API key. Configure OpenAI API key for full chat capabilities. In the meantime, I can still help you with system commands!"
    
    def get_response(self, message):
        """
        Get AI response (alias for chat)
        
        Args:
            message: User message
            
        Returns:
            AI response
        """
        return self.chat(message)
    
    def speak_response(self, message, voice_engine=None):
        """
        Get response and speak it
        
        Args:
            message: User message
            voice_engine: Voice engine for TTS
            
        Returns:
            AI response
        """
        response = self.chat(message)
        
        if voice_engine:
            voice_engine.speak(response)
        
        return response
    
    def get_conversation_summary(self):
        """
        Get summary of conversation
        
        Returns:
            Summary string
        """
        if not self.conversation_history:
            return "No conversation history."
        
        summary = f"Conversation has {len(self.conversation_history)} messages."
        
        user_messages = [m for m in self.conversation_history if m['role'] == 'user']
        assistant_messages = [m for m in self.conversation_history if m['role'] == 'assistant']
        
        summary += f" {len(user_messages)} from user, {len(assistant_messages)} from assistant."
        
        return summary
    
    def save_conversation(self, file_path):
        """
        Save conversation to file
        
        Args:
            file_path: Path to save
            
        Returns:
            True if successful
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving conversation: {e}")
            return False
    
    def load_conversation(self, file_path):
        """
        Load conversation from file
        
        Args:
            file_path: Path to load
            
        Returns:
            True if successful
        """
        try:
            with open(file_path, 'r') as f:
                self.conversation_history = json.load(f)
            return True
        except Exception as e:
            self.logger.error(f"Error loading conversation: {e}")
            return False


# ============================================
# Main function for testing
# ============================================

def test_chat_module():
    """Test chat module"""
    print("Testing Chat Module...")
    
    chat = ChatModule()
    
    # Test conversation
    messages = [
        "Hello!",
        "How are you?",
        "What can you do?",
        "Thank you!"
    ]
    
    print("\n" + "="*60)
    print("Testing Chat:")
    print("="*60)
    
    for msg in messages:
        print(f"\nUser: {msg}")
        response = chat.chat(msg)
        print(f"Assistant: {response}")
    
    # Test conversation summary
    print("\n" + "="*60)
    print("Conversation Summary:")
    print("="*60)
    print(chat.get_conversation_summary())
    
    return chat


if __name__ == "__main__":
    test_chat_module()
