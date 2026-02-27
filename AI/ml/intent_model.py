"""
Intent Classification Model Module
ML-based intent classification using TF-IDF and Logistic Regression/Random Forest
"""

import json
import pickle
import logging
import os
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import sys

# Import config
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class IntentClassifier:
    """
    ML-based Intent Classification
    Uses TF-IDF vectorization and ML classifier
    """
    
    def __init__(self, intents_file=None, model_path=None, vectorizer_path=None):
        """
        Initialize intent classifier
        
        Args:
            intents_file: Path to intents JSON file
            model_path: Path to saved model
            vectorizer_path: Path to saved vectorizer
        """
        self.logger = logging.getLogger('DesktopAssistant.IntentClassifier')
        self.intents_file = intents_file or config.INTENTS_FILE
        self.model_path = model_path or config.TRAINED_MODEL_PATH
        self.vectorizer_path = vectorizer_path or config.VECTORIZER_PATH
        
        self.model = None
        self.vectorizer = None
        self.intents = []
        self.confidence_threshold = config.INTENT_CONFIDENCE_THRESHOLD
        
        # Load intents and train/load model
        self._load_intents()
        self._load_model()
        
        self.logger.info("Intent Classifier initialized")
    
    def _load_intents(self):
        """Load intents from JSON file"""
        if os.path.exists(self.intents_file):
            try:
                with open(self.intents_file, 'r') as f:
                    data = json.load(f)
                    self.intents = data.get('intents', [])
                self.logger.info(f"Loaded {len(self.intents)} intent patterns")
            except Exception as e:
                self.logger.error(f"Failed to load intents: {e}")
                self.intents = self._get_default_intents()
        else:
            self.logger.warning("Intents file not found, using defaults")
            self.intents = self._get_default_intents()
    
    def _get_default_intents(self):
        """Get default intents if file not found"""
        return [
            {
                "tag": "open_app",
                "patterns": ["open app", "launch application", "start program", "open chrome", "open notepad", "open calculator"],
                "responses": ["Opening application..."]
            },
            {
                "tag": "system_status",
                "patterns": ["system status", "check system", "how are you", "system info", "computer status"],
                "responses": ["Here is your system status..."]
            },
            {
                "tag": "weather",
                "patterns": ["weather", "temperature", "forecast", "how is the weather", "is it raining"],
                "responses": ["Let me check the weather..."]
            },
            {
                "tag": "news",
                "patterns": ["news", "headlines", "latest news", "what's happening", "today's news"],
                "responses": ["Fetching latest news..."]
            },
            {
                "tag": "reminder",
                "patterns": ["remind me", "set reminder", "reminder", " remind ", "alarm"],
                "responses": ["Setting reminder..."]
            },
            {
                "tag": "chat",
                "patterns": ["chat", "talk", "conversation", "hello", "hi", "hey"],
                "responses": ["Hello! How can I help?"]
            }
        ]
    
    def _load_model(self):
        """Load trained model if exists"""
        if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(self.vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                self.logger.info("Loaded existing model and vectorizer")
            except Exception as e:
                self.logger.error(f"Failed to load model: {e}")
                self.train()
        else:
            self.logger.info("No trained model found, training new model")
            self.train()
    
    def _prepare_training_data(self):
        """Prepare training data from intents"""
        X = []  # Features (text)
        y = []  # Labels (intents)
        
        for intent in self.intents:
            tag = intent.get('tag')
            patterns = intent.get('patterns', [])
            
            for pattern in patterns:
                X.append(pattern.lower())
                y.append(tag)
        
        return X, y
    
    def train(self, use_random_forest=None):
        """
        Train the intent classification model
        
        Args:
            use_random_forest: Use Random Forest instead of Logistic Regression
        """
        self.logger.info("Training intent classification model...")
        
        X, y = self._prepare_training_data()
        
        if not X:
            self.logger.error("No training data available")
            return
        
        # Create vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=config.MAX_FEATURES,
            ngram_range=config.N_GRAMS,
            stop_words='english'
        )
        
        # Transform text to TF-IDF features
        X_tfidf = self.vectorizer.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_tfidf, y, test_size=0.2, random_state=42
        )
        
        # Train model
        if use_random_forest is None:
            use_random_forest = config.USE_RANDOM_FOREST
        
        if use_random_forest:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
        else:
            self.model = LogisticRegression(
                max_iter=1000,
                random_state=42,
                multi_class='multinomial'
            )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        self.logger.info(f"Model training complete. Accuracy: {accuracy:.2f}")
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_tfidf, y, cv=5)
        self.logger.info(f"Cross-validation scores: {cv_scores}")
        self.logger.info(f"Mean CV accuracy: {cv_scores.mean():.2f} (+/- {cv_scores.std()*2:.2f})")
        
        # Save model
        self._save_model()
        
        # Log classification report
        self.logger.info("\n" + classification_report(y_test, y_pred))
    
    def _save_model(self):
        """Save trained model and vectorizer"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            with open(self.vectorizer_path, 'wb') as f:
                pickle.dump(self.vectorizer, f)
            
            self.logger.info("Model saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save model: {e}")
    
    def predict(self, text):
        """
        Predict intent from text
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (intent_tag, confidence_score)
        """
        if not self.model or not self.vectorizer:
            self.logger.error("Model not loaded")
            return None, 0.0
        
        try:
            # Transform input text
            X_tfidf = self.vectorizer.transform([text.lower()])
            
            # Get prediction
            intent = self.model.predict(X_tfidf)[0]
            
            # Get confidence scores
            probabilities = self.model.predict_proba(X_tfidf)[0]
            classes = self.model.classes_
            confidence = probabilities[classes.tolist().index(intent)]
            
            return intent, float(confidence)
        
        except Exception as e:
            self.logger.error(f"Prediction error: {e}")
            return None, 0.0
    
    def predict_with_confidence(self, text):
        """
        Predict with full confidence details
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with intent and all confidence scores
        """
        if not self.model or not self.vectorizer:
            return {'intent': None, 'confidence': 0.0, 'all_scores': {}}
        
        try:
            X_tfidf = self.vectorizer.transform([text.lower()])
            probabilities = self.model.predict_proba(X_tfidf)[0]
            classes = self.model.classes_
            
            # Create confidence dictionary
            all_scores = {
                str(cls): float(prob) 
                for cls, prob in zip(classes, probabilities)
            }
            
            intent = self.model.predict(X_tfidf)[0]
            confidence = all_scores.get(intent, 0.0)
            
            return {
                'intent': intent,
                'confidence': confidence,
                'all_scores': all_scores,
                'is_confident': confidence >= self.confidence_threshold
            }
        
        except Exception as e:
            self.logger.error(f"Prediction error: {e}")
            return {'intent': None, 'confidence': 0.0, 'all_scores': {}}
    
    def get_confusion_matrix(self, X_test=None, y_test=None):
        """
        Get confusion matrix for the model
        
        Args:
            X_test: Test features
            y_test: Test labels
            
        Returns:
            Confusion matrix
        """
        if not self.model or not self.vectorizer:
            return None
        
        X, y = self._prepare_training_data()
        X_tfidf = self.vectorizer.transform(X)
        
        if X_test is None or y_test is None:
            X_train, X_test, y_train, y_test = train_test_split(
                X_tfidf, y, test_size=0.2, random_state=42
            )
        
        y_pred = self.model.predict(X_test)
        
        return confusion_matrix(y_test, y_pred, labels=self.model.classes_)
    
    def get_top_intents(self, text, top_n=3):
        """
        Get top N predicted intents
        
        Args:
            text: Input text
            top_n: Number of top intents to return
            
        Returns:
            List of tuples (intent, confidence)
        """
        result = self.predict_with_confidence(text)
        all_scores = result.get('all_scores', {})
        
        sorted_scores = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_scores[:top_n]
    
    def add_intent(self, tag, patterns, responses):
        """
        Add new intent
        
        Args:
            tag: Intent tag
            patterns: List of example patterns
            responses: List of possible responses
        """
        # Check if intent already exists
        for intent in self.intents:
            if intent['tag'] == tag:
                # Update existing
                intent['patterns'].extend(patterns)
                intent['responses'].extend(responses)
                break
        else:
            # Add new intent
            self.intents.append({
                'tag': tag,
                'patterns': patterns,
                'responses': responses
            })
        
        # Save intents
        self._save_intents()
        
        # Retrain model
        self.train()
    
    def _save_intents(self):
        """Save intents to JSON file"""
        try:
            with open(self.intents_file, 'w') as f:
                json.dump({'intents': self.intents}, f, indent=2)
            self.logger.info("Intents saved")
        except Exception as e:
            self.logger.error(f"Failed to save intents: {e}")
    
    def get_available_intents(self):
        """Get list of available intent tags"""
        return [intent['tag'] for intent in self.intents]
    
    def get_intent_info(self, tag):
        """Get intent information"""
        for intent in self.intents:
            if intent['tag'] == tag:
                return intent
        return None
    
    def get_training_data_stats(self):
        """Get statistics about training data"""
        stats = {
            'total_patterns': sum(len(i.get('patterns', [])) for i in self.intents),
            'total_intents': len(self.intents),
            'intents': {}
        }
        
        for intent in self.intents:
            stats['intents'][intent['tag']] = len(intent.get('patterns', []))
        
        return stats


# ============================================
# Main function for testing
# ============================================

def test_intent_classifier():
    """Test intent classifier"""
    print("Testing Intent Classifier...")
    
    classifier = IntentClassifier()
    
    # Get stats
    stats = classifier.get_training_data_stats()
    print(f"\nTraining data stats: {stats}")
    
    # Test predictions
    test_commands = [
        "open notepad",
        "what's the weather",
        "set reminder for tomorrow",
        "read the news",
        "how is my system",
        "chat with me",
        "delete the file"
    ]
    
    print("\n" + "="*60)
    print("Testing predictions:")
    print("="*60)
    
    for command in test_commands:
        result = classifier.predict_with_confidence(command)
        print(f"\nCommand: '{command}'")
        print(f"  Intent: {result['intent']}")
        print(f"  Confidence: {result['confidence']:.3f}")
        print(f"  Is confident: {result['is_confident']}")
        print(f"  Top 3: {classifier.get_top_intents(command)}")
    
    # Get confusion matrix
    print("\n" + "="*60)
    print("Confusion Matrix:")
    print("="*60)
    cm = classifier.get_confusion_matrix()
    if cm is not None:
        print(cm)
    
    return classifier


if __name__ == "__main__":
    test_intent_classifier()
