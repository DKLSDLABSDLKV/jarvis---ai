"""
Sentiment Analysis Module for Secure Intelligent Desktop Assistant
Uses NLTK/Vader for sentiment analysis
"""

import logging
from pathlib import Path
import sys
from textblob import TextBlob

# Try to import NLTK Vader
try:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK not available, using TextBlob for sentiment")

# Import config
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class SentimentAnalyzer:
    """
    Sentiment Analysis for user input
    Uses NLTK Vader or TextBlob for sentiment detection
    """
    
    def __init__(self):
        """Initialize sentiment analyzer"""
        self.logger = logging.getLogger('DesktopAssistant.Sentiment')
        self.vader = None
        self.positive_threshold = config.POSITIVE_THRESHOLD
        self.negative_threshold = config.NEGATIVE_THRESHOLD
        
        # Initialize NLTK Vader
        if NLTK_AVAILABLE:
            try:
                self.vader = SentimentIntensityAnalyzer()
                self.logger.info("NLTK Vader sentiment analyzer initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Vader: {e}")
        
        self.logger.info("Sentiment Analyzer initialized")
    
    def analyze(self, text):
        """
        Analyze sentiment of text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with sentiment scores
        """
        result = {
            'text': text,
            'sentiment': 'neutral',
            'polarity': 0.0,
            'subjectivity': 0.0,
            'confidence': 0.0,
            'vader_scores': None
        }
        
        # Use TextBlob
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            result['polarity'] = polarity
            result['subjectivity'] = subjectivity
            
            # Determine sentiment category
            if polarity > self.positive_threshold:
                result['sentiment'] = 'positive'
            elif polarity < self.negative_threshold:
                result['sentiment'] = 'negative'
            else:
                result['sentiment'] = 'neutral'
            
            # Confidence based on absolute polarity
            result['confidence'] = abs(polarity)
            
        except Exception as e:
            self.logger.error(f"TextBlob sentiment error: {e}")
        
        # Use NLTK Vader if available
        if self.vader:
            try:
                vader_scores = self.vader.polarity_scores(text)
                result['vader_scores'] = vader_scores
                
                # Override sentiment if Vader is more confident
                compound = vader_scores.get('compound', 0)
                if abs(compound) > result['confidence']:
                    result['confidence'] = abs(compound)
                    if compound > 0.05:
                        result['sentiment'] = 'positive'
                    elif compound < -0.05:
                        result['sentiment'] = 'negative'
                    else:
                        result['sentiment'] = 'neutral'
                        
            except Exception as e:
                self.logger.error(f"Vader sentiment error: {e}")
        
        return result
    
    def is_positive(self, text):
        """Check if text has positive sentiment"""
        result = self.analyze(text)
        return result['sentiment'] == 'positive'
    
    def is_negative(self, text):
        """Check if text has negative sentiment"""
        result = self.analyze(text)
        return result['sentiment'] == 'negative'
    
    def is_neutral(self, text):
        """Check if text has neutral sentiment"""
        result = self.analyze(text)
        return result['sentiment'] == 'neutral'
    
    def get_polarity(self, text):
        """Get polarity score (-1 to 1)"""
        result = self.analyze(text)
        return result['polarity']
    
    def adjust_response_for_sentiment(self, base_response, sentiment_result):
        """
        Adjust assistant response based on user sentiment
        
        Args:
            base_response: The planned response
            sentiment_result: Result from analyze()
            
        Returns:
            Adjusted response
        """
        sentiment = sentiment_result['sentiment']
        confidence = sentiment_result.get('confidence', 0.5)
        
        # Only adjust if confident enough
        if confidence < 0.3:
            return base_response
        
        if sentiment == 'positive':
            # Add enthusiastic acknowledgment
            additions = [
                " I'm glad to hear that!",
                " That's wonderful!",
                " Great to know!",
                " Awesome!"
            ]
            import random
            return base_response + random.choice(additions)
        
        elif sentiment == 'negative':
            # Add empathetic acknowledgment
            additions = [
                " I understand.",
                " I'm sorry to hear that.",
                " Don't worry, I'll help you with this.",
                " Let's work through this together."
            ]
            import random
            return base_response + random.choice(additions)
        
        return base_response
    
    def analyze_conversation(self, messages):
        """
        Analyze sentiment across a conversation
        
        Args:
            messages: List of message strings
            
        Returns:
            Dictionary with overall analysis
        """
        if not messages:
            return {
                'overall_sentiment': 'neutral',
                'average_polarity': 0.0,
                'message_count': 0
            }
        
        sentiments = []
        polarities = []
        
        for msg in messages:
            result = self.analyze(msg)
            sentiments.append(result['sentiment'])
            polarities.append(result['polarity'])
        
        avg_polarity = sum(polarities) / len(polarities)
        
        # Determine overall sentiment
        sentiment_counts = {}
        for s in sentiments:
            sentiment_counts[s] = sentiment_counts.get(s, 0) + 1
        
        overall = max(sentiment_counts, key=sentiment_counts.get)
        
        return {
            'overall_sentiment': overall,
            'average_polarity': avg_polarity,
            'message_count': len(messages),
            'sentiment_distribution': sentiment_counts
        }
    
    def get_emotion_indicators(self, text):
        """
        Detect emotion indicators in text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of emotion indicators
        """
        text_lower = text.lower()
        
        emotions = {
            'happy': ['happy', 'glad', 'pleased', 'delighted', 'thrilled', 'excited'],
            'sad': ['sad', 'unhappy', 'upset', 'depressed', 'disappointed'],
            'angry': ['angry', 'mad', 'furious', 'annoyed', 'frustrated'],
            'fearful': ['afraid', 'scared', 'worried', 'nervous', 'anxious'],
            'surprised': ['surprised', 'amazed', 'astonished', 'shocked'],
            'neutral': []
        }
        
        detected = {}
        
        for emotion, keywords in emotions.items():
            if not emotion == 'neutral':
                count = sum(1 for kw in keywords if kw in text_lower)
                if count > 0:
                    detected[emotion] = count
        
        return detected
    
    def get_sentiment_report(self, text):
        """
        Get comprehensive sentiment report
        
        Args:
            text: Input text
            
        Returns:
            Detailed sentiment report dictionary
        """
        analysis = self.analyze(text)
        emotions = self.get_emotion_indicators(text)
        
        report = {
            'text': text[:100] + '...' if len(text) > 100 else text,
            'sentiment': analysis['sentiment'],
            'polarity': round(analysis['polarity'], 3),
            'subjectivity': round(analysis['subjectivity'], 3),
            'confidence': round(analysis['confidence'], 3),
            'emotions': emotions,
            'vader': analysis.get('vader_scores')
        }
        
        return report


# ============================================
# Main function for testing
# ============================================

def test_sentiment():
    """Test sentiment analyzer"""
    print("Testing Sentiment Analyzer...")
    
    analyzer = SentimentAnalyzer()
    
    test_texts = [
        "I'm so happy today! Everything is great!",
        "This is terrible. I hate it.",
        "The weather is okay.",
        "I'm worried about the meeting tomorrow.",
        "That's amazing news! I'm so excited!",
        "I'm feeling a bit neutral about this.",
        "Don't worry, everything will be fine.",
    ]
    
    print("\n" + "="*60)
    print("Sentiment Analysis Results:")
    print("="*60)
    
    for text in test_texts:
        result = analyzer.analyze(text)
        print(f"\nText: {text}")
        print(f"  Sentiment: {result['sentiment']}")
        print(f"  Polarity: {result['polarity']:.3f}")
        print(f"  Subjectivity: {result['subjectivity']:.3f}")
        print(f"  Confidence: {result['confidence']:.3f}")
        print(f"  Emotions: {analyzer.get_emotion_indicators(text)}")
    
    # Test response adjustment
    print("\n" + "="*60)
    print("Response Adjustment Examples:")
    print("="*60)
    
    base_response = "I'll help you with that."
    
    for text in test_texts[:3]:
        sentiment = analyzer.analyze(text)
        adjusted = analyzer.adjust_response_for_sentiment(base_response, sentiment)
        print(f"\nOriginal: {base_response}")
        print(f"User said: {text}")
        print(f"Adjusted: {adjusted}")
    
    return analyzer


if __name__ == "__main__":
    test_sentiment()
