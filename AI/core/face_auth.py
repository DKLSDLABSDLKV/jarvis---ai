"""
Face Authentication Module for Secure Intelligent Desktop Assistant
Handles face recognition login using webcam
"""

# Try to import required libraries, make face recognition optional
try:
    import cv2
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    cv2 = None
    face_recognition = None

import numpy as np
import pickle
import logging
import os
from pathlib import Path
from datetime import datetime
import sys

# Import config
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class FaceAuthenticator:
    """
    Face Recognition Authentication System
    Handles face enrollment, verification, and login
    """
    
    def __init__(self, encodings_file=None, tolerance=None):
        """
        Initialize face authenticator
        
        Args:
            encodings_file: Path to face encodings file
            tolerance: Face matching tolerance (lower = more strict)
        """
        self.logger = logging.getLogger('DesktopAssistant.FaceAuth')
        
        if not FACE_RECOGNITION_AVAILABLE:
            self.logger.warning("Face recognition not available. Install dlib and face-recognition for full functionality.")
        
        self.encodings_file = encodings_file or config.ENCODINGS_FILE
        self.tolerance = tolerance or config.FACE_TOLERANCE
        
        # Known face encodings and names
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_metadata = {}  # Additional info about faces
        
        # Video capture
        self.video_capture = None
        
        # Load existing encodings
        self._load_encodings()
        
        self.logger.info("Face Authenticator initialized")
    
    def is_available(self):
        """Check if face recognition is available"""
        return FACE_RECOGNITION_AVAILABLE
    
    def _load_encodings(self):
        """Load face encodings from file"""
        if not FACE_RECOGNITION_AVAILABLE:
            return
            
        if os.path.exists(self.encodings_file):
            try:
                with open(self.encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data.get('encodings', [])
                    self.known_face_names = data.get('names', [])
                    self.known_face_metadata = data.get('metadata', {})
                self.logger.info(f"Loaded {len(self.known_face_names)} face encodings")
            except Exception as e:
                self.logger.error(f"Failed to load face encodings: {e}")
        else:
            self.logger.info("No existing face encodings found")
    
    def _save_encodings(self):
        """Save face encodings to file"""
        if not FACE_RECOGNITION_AVAILABLE:
            return
            
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.encodings_file), exist_ok=True)
            
            with open(self.encodings_file, 'wb') as f:
                pickle.dump({
                    'encodings': self.known_face_encodings,
                    'names': self.known_face_names,
                    'metadata': self.known_face_metadata
                }, f)
            self.logger.info("Face encodings saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save face encodings: {e}")
    
    def enroll_face(self, name, role=None, additional_info=None):
        """
        Enroll a new face
        
        Args:
            name: Name of the person
            role: User role (admin, user, guest)
            additional_info: Additional metadata
            
        Returns:
            True if enrollment successful, False otherwise
        """
        if not FACE_RECOGNITION_AVAILABLE:
            self.logger.warning("Face recognition not available")
            return False
            
        self.logger.info(f"Enrolling new face for: {name}")
        
        # Initialize video capture
        video_capture = cv2.VideoCapture(0)
        
        if not video_capture.isOpened():
            self.logger.error("Failed to open video capture")
            return False
        
        enrolled = False
        encodings = []
        
        # Capture multiple frames for better accuracy
        self.speak("Please look at the camera. I'll capture your face.")
        
        for i in range(5):
            ret, frame = video_capture.read()
            if not ret:
                continue
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find faces
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)
            
            if face_encoding:
                encodings.extend(face_encoding)
                self.speak(f"Captured {i+1}/5")
        
        video_capture.release()
        
        if encodings:
            # Use the best encoding (first one with highest confidence)
            # For simplicity, use average of all encodings
            avg_encoding = np.mean(encodings, axis=0)
            
            self.known_face_encodings.append(avg_encoding)
            self.known_face_names.append(name)
            
            # Store metadata
            self.known_face_metadata[name] = {
                'role': role or 'user',
                'enrolled_at': datetime.now().isoformat(),
                'additional_info': additional_info or {}
            }
            
            self._save_encodings()
            enrolled = True
            self.logger.info(f"Successfully enrolled face for: {name}")
            self.speak(f"Face enrolled successfully for {name}")
        else:
            self.logger.warning(f"No face detected for enrollment: {name}")
            self.speak("No face detected. Please try again.")
        
        return enrolled
    
    def verify_face(self, show_preview=False):
        """
        Verify face against enrolled faces
        
        Args:
            show_preview: Whether to show video preview
            
        Returns:
            Tuple of (success: bool, name: str or None, confidence: float)
        """
        if not FACE_RECOGNITION_AVAILABLE:
            self.logger.warning("Face recognition not available")
            return False, None, 0.0
            
        self.logger.info("Starting face verification")
        
        # Initialize video capture
        video_capture = cv2.VideoCapture(0)
        
        if not video_capture.isOpened():
            self.logger.error("Failed to open video capture")
            return False, None, 0.0
        
        if not self.known_face_encodings:
            self.logger.warning("No enrolled faces to verify against")
            video_capture.release()
            return False, None, 0.0
        
        recognized = False
        matched_name = None
        best_confidence = 0.0
        
        # Small delay for camera to warm up
        import time
        time.sleep(0.5)
        
        # Try to recognize face
        ret, frame = video_capture.read()
        if ret:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find faces
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            if face_encodings:
                # Compare with known faces
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(
                        self.known_face_encodings, 
                        face_encoding, 
                        self.tolerance
                    )
                    
                    face_distances = face_recognition.face_distance(
                        self.known_face_encodings, 
                        face_encoding
                    )
                    
                    if len(face_distances) > 0:
                        best_match_index = np.argmin(face_distances)
                        
                        if matches[best_match_index]:
                            recognized = True
                            matched_name = self.known_face_names[best_match_index]
                            # Confidence is inverse of distance
                            best_confidence = 1.0 - face_distances[best_match_index]
                            break
        
        video_capture.release()
        
        if recognized:
            self.logger.info(f"Face verified: {matched_name} (confidence: {best_confidence:.2f})")
        else:
            self.logger.warning("Face not recognized")
        
        return recognized, matched_name, best_confidence
    
    def authenticate(self, max_attempts=3):
        """
        Full authentication process with video preview
        
        Args:
            max_attempts: Maximum number of verification attempts
            
        Returns:
            Tuple of (success: bool, name: str or None)
        """
        self.logger.info("Starting authentication process")
        
        if not FACE_RECOGNITION_AVAILABLE:
            # Bypass authentication if face recognition not available
            self.logger.warning("Face recognition not available - bypassing authentication")
            return True, "guest"
        
        if not self.known_face_encodings:
            self.logger.warning("No enrolled faces - authentication bypassed")
            return True, "guest"  # Bypass if no faces enrolled
        
        for attempt in range(max_attempts):
            self.speak(f"Please look at the camera. Attempt {attempt + 1} of {max_attempts}")
            
            success, name, confidence = self.verify_face(show_preview=False)
            
            if success:
                self.logger.info(f"Authentication successful: {name} (confidence: {confidence:.2f})")
                self.speak(f"Welcome, {name}!")
                return True, name
            
            if attempt < max_attempts - 1:
                self.speak("Face not recognized. Please try again.")
        
        self.logger.warning(f"Authentication failed after {max_attempts} attempts")
        self.speak("Authentication failed. Access denied.")
        return False, None
    
    def remove_face(self, name):
        """
        Remove enrolled face
        
        Args:
            name: Name of the person to remove
            
        Returns:
            True if removed, False otherwise
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return False
            
        if name in self.known_face_names:
            index = self.known_face_names.index(name)
            self.known_face_encodings.pop(index)
            self.known_face_names.pop(index)
            
            if name in self.known_face_metadata:
                del self.known_face_metadata[name]
            
            self._save_encodings()
            self.logger.info(f"Removed face for: {name}")
            return True
        
        return False
    
    def list_enrolled_faces(self):
        """Get list of enrolled faces"""
        return [(name, self.known_face_metadata.get(name, {})) 
                for name in self.known_face_names]
    
    def speak(self, text):
        """Speak text (imports VoiceEngine if available)"""
        try:
            from core.voice import VoiceEngine
            voice = VoiceEngine()
            voice.speak(text)
        except:
            print(f"[TTS] {text}")
    
    def capture_and_save_image(self, name):
        """
        Capture and save an image of the user
        
        Args:
            name: Name to save the image as
            
        Returns:
            Path to saved image or None
        """
        if not FACE_RECOGNITION_AVAILABLE or cv2 is None:
            return None
            
        video_capture = cv2.VideoCapture(0)
        
        if not video_capture.isOpened():
            return None
        
        ret, frame = video_capture.read()
        video_capture.release()
        
        if ret:
            # Save image
            image_path = config.AUTHORIZED_FACES_DIR / f"{name}.jpg"
            cv2.imwrite(str(image_path), frame)
            return str(image_path)
        
        return None
    
    def get_face_statistics(self):
        """Get statistics about enrolled faces"""
        return {
            'total_faces': len(self.known_face_names),
            'available': FACE_RECOGNITION_AVAILABLE,
            'faces_by_role': {
                meta.get('role', 'unknown'): sum(
                    1 for m in self.known_face_metadata.values() 
                    if m.get('role') == meta.get('role')
                )
                for meta in [self.known_face_metadata.get(name, {}) 
                            for name in self.known_face_names]
            }
        }


# ============================================
# Main function for testing
# ============================================

def test_face_auth():
    """Test face authentication"""
    print("Testing Face Authentication...")
    
    auth = FaceAuthenticator()
    
    if not auth.is_available():
        print("WARNING: Face recognition not available. Install dlib for full functionality.")
    
    # List enrolled faces
    faces = auth.list_enrolled_faces()
    print(f"\nEnrolled faces: {len(faces)}")
    for name, metadata in faces:
        print(f"  - {name}: {metadata}")
    
    # Note: Requires webcam for actual testing
    print("\nNote: Full testing requires webcam")
    
    return auth


if __name__ == "__main__":
    test_face_auth()
