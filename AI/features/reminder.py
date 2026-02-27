"""
Reminder Manager Module for Secure Intelligent Desktop Assistant
Schedule and manage reminders via voice commands
"""

import json
import logging
import threading
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Import config
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class ReminderManager:
    """
    Reminder Scheduling System
    Manages voice reminders with scheduling and notifications
    """
    
    def __init__(self, reminders_file=None):
        """
        Initialize reminder manager
        
        Args:
            reminders_file: Path to reminders JSON file
        """
        self.logger = logging.getLogger('DesktopAssistant.ReminderManager')
        self.reminders_file = reminders_file or config.REMINDERS_FILE
        self.reminders = []
        self.voice_engine = None
        self.is_running = False
        
        # Load existing reminders
        self._load_reminders()
        
        self.logger.info("Reminder Manager initialized")
    
    def _load_reminders(self):
        """Load reminders from file"""
        if Path(self.reminders_file).exists():
            try:
                with open(self.reminders_file, 'r') as f:
                    self.reminders = json.load(f)
                self.logger.info(f"Loaded {len(self.reminders)} reminders")
            except Exception as e:
                self.logger.error(f"Failed to load reminders: {e}")
                self.reminders = []
        else:
            self.reminders = []
    
    def _save_reminders(self):
        """Save reminders to file"""
        try:
            # Create directory if needed
            Path(self.reminders_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.reminders_file, 'w') as f:
                json.dump(self.reminders, f, indent=2)
            
            self.logger.debug("Reminders saved")
        except Exception as e:
            self.logger.error(f"Failed to save reminders: {e}")
    
    def _add_reminder(self, reminder):
        """
        Add a reminder
        
        Args:
            reminder: Reminder dictionary
            
        Returns:
            Reminder ID
        """
        reminder_id = len(self.reminders) + 1
        reminder['id'] = reminder_id
        reminder['created_at'] = datetime.now().isoformat()
        reminder['completed'] = False
        
        self.reminders.append(reminder)
        self._save_reminders()
        
        return reminder_id
    
    def set_reminder(self, message, time_str=None, minutes=None, hours=None, days=None, voice_engine=None):
        """
        Set a reminder
        
        Args:
            message: Reminder message
            time_str: Time string (e.g., "3pm", "14:30")
            minutes: Minutes from now
            hours: Hours from now
            days: Days from now
            voice_engine: Voice engine for notification
            
        Returns:
            Reminder ID
        """
        self.voice_engine = voice_engine
        
        # Calculate reminder time
        if time_str:
            reminder_time = self._parse_time_string(time_str)
        elif minutes or hours or days:
            reminder_time = datetime.now()
            if minutes:
                reminder_time += timedelta(minutes=minutes)
            if hours:
                reminder_time += timedelta(hours=hours)
            if days:
                reminder_time += timedelta(days=days)
        else:
            # Default to 1 hour from now
            reminder_time = datetime.now() + timedelta(hours=1)
        
        reminder = {
            'message': message,
            'reminder_time': reminder_time.isoformat(),
            'voice_engine': voice_engine
        }
        
        reminder_id = self._add_reminder(reminder)
        
        self.logger.info(f"Reminder set for {reminder_time}: {message}")
        
        return reminder_id
    
    def _parse_time_string(self, time_str):
        """Parse time string to datetime"""
        now = datetime.now()
        
        # Handle various formats
        time_str = time_str.lower().strip()
        
        # Check for specific times
        if 'am' in time_str or 'pm' in time_str:
            # Convert 12-hour to 24-hour
            try:
                hour = int(time_str.replace('am', '').replace('pm', '').strip())
                if 'pm' in time_str and hour < 12:
                    hour += 12
                if 'am' in time_str and hour == 12:
                    hour = 0
                return now.replace(hour=hour, minute=0, second=0)
            except:
                pass
        
        # Check for HH:MM format
        if ':' in time_str:
            try:
                parts = time_str.split(':')
                hour = int(parts[0])
                minute = int(parts[1])
                return now.replace(hour=hour, minute=minute, second=0)
            except:
                pass
        
        # Default: set for today at the given time
        return now + timedelta(hours=1)
    
    def get_pending_reminders(self):
        """
        Get pending reminders
        
        Returns:
            List of pending reminders
        """
        now = datetime.now()
        
        pending = []
        for reminder in self.reminders:
            if not reminder.get('completed', False):
                reminder_time = datetime.fromisoformat(reminder['reminder_time'])
                if reminder_time > now:
                    pending.append(reminder)
        
        return pending
    
    def get_all_reminders(self):
        """Get all reminders"""
        return self.reminders
    
    def complete_reminder(self, reminder_id):
        """
        Mark reminder as completed
        
        Args:
            reminder_id: Reminder ID
            
        Returns:
            True if successful
        """
        for reminder in self.reminders:
            if reminder.get('id') == reminder_id:
                reminder['completed'] = True
                self._save_reminders()
                return True
        return False
    
    def delete_reminder(self, reminder_id):
        """
        Delete a reminder
        
        Args:
            reminder_id: Reminder ID
            
        Returns:
            True if successful
        """
        self.reminders = [r for r in self.reminders if r.get('id') != reminder_id]
        self._save_reminders()
        return True
    
    def cancel_all_reminders(self):
        """Cancel all reminders"""
        self.reminders = []
        self._save_reminders()
    
    def check_due_reminders(self):
        """Check for due reminders and trigger notification"""
        now = datetime.now()
        
        for reminder in self.reminders:
            if not reminder.get('completed', False):
                reminder_time = datetime.fromisoformat(reminder['reminder_time'])
                
                if reminder_time <= now:
                    # Reminder is due
                    self._trigger_reminder(reminder)
                    
                    # Mark as completed
                    reminder['completed'] = True
        
        self._save_reminders()
    
    def _trigger_reminder(self, reminder):
        """
        Trigger reminder notification
        
        Args:
            reminder: Reminder dictionary
        """
        message = f"Reminder: {reminder['message']}"
        
        self.logger.info(f"Triggering reminder: {message}")
        
        if self.voice_engine:
            self.voice_engine.speak(message)
        else:
            print(message)
    
    def set_voice_engine(self, voice_engine):
        """Set voice engine for notifications"""
        self.voice_engine = voice_engine
    
    def start_scheduler(self):
        """Start the reminder scheduler"""
        self.is_running = True
        
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                self.check_due_reminders()
                time.sleep(1)
        
        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()
        
        self.logger.info("Reminder scheduler started")
        return thread
    
    def stop_scheduler(self):
        """Stop the reminder scheduler"""
        self.is_running = False
        self.logger.info("Reminder scheduler stopped")
    
    def get_reminder_stats(self):
        """Get reminder statistics"""
        total = len(self.reminders)
        completed = sum(1 for r in self.reminders if r.get('completed', False))
        pending = total - completed
        
        return {
            'total': total,
            'completed': completed,
            'pending': pending
        }
    
    def speak_upcoming_reminders(self, voice_engine=None):
        """
        Speak upcoming reminders
        
        Args:
            voice_engine: Voice engine for TTS
        """
        pending = self.get_pending_reminders()
        
        if not pending:
            if voice_engine:
                voice_engine.speak("You have no upcoming reminders.")
            return
        
        message = f"You have {len(pending)} upcoming reminders. "
        
        for i, reminder in enumerate(pending[:3], 1):
            reminder_time = datetime.fromisoformat(reminder['reminder_time'])
            time_str = reminder_time.strftime("%I:%M %p")
            message += f"{i}. {reminder['message']} at {time_str}. "
        
        if voice_engine:
            voice_engine.speak(message)
        
        return message


# ============================================
# Main function for testing
# ============================================

def test_reminder_manager():
    """Test reminder manager"""
    print("Testing Reminder Manager...")
    
    manager = ReminderManager()
    
    # Set some reminders
    print("\nSetting reminders...")
    
    id1 = manager.set_reminder("Meeting in 30 seconds", minutes=0)
    print(f"Set reminder 1 (ID: {id1})")
    
    id2 = manager.set_reminder("Take a break", minutes=1)
    print(f"Set reminder 2 (ID: {id2})")
    
    id3 = manager.set_reminder("Call John", hours=2)
    print(f"Set reminder 3 (ID: {id3})")
    
    # Get pending
    print("\nPending reminders:")
    for reminder in manager.get_pending_reminders():
        print(f"  - {reminder}")
    
    # Get stats
    print("\nStats:", manager.get_reminder_stats())
    
    # Start scheduler
    print("\nStarting scheduler (will check for due reminders)...")
    manager.start_scheduler()
    
    # Wait a bit
    print("Waiting for reminders...")
    time.sleep(3)
    
    # Stop scheduler
    manager.stop_scheduler()
    
    print("\nTest complete!")
    
    return manager


if __name__ == "__main__":
    test_reminder_manager()
