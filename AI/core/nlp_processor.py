"""
NLP Processor Module for Secure Intelligent Desktop Assistant
Uses spaCy for offline NLP: tokenization, lemmatization, entity recognition
"""

# Try to import spaCy, make it optional
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None

import logging
from pathlib import Path
import sys
import re

# Import config
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class NLPProcessor:
    """
    Offline NLP Processing using spaCy
    Handles tokenization, lemmatization, POS tagging, and entity recognition
    """
    
    def __init__(self, model_name="en_core_web_sm"):
        """
        Initialize NLP processor
        
        Args:
            model_name: spaCy model name to load
        """
        self.logger = logging.getLogger('DesktopAssistant.NLP')
        self.nlp = None
        
        if SPACY_AVAILABLE:
            self._load_model(model_name)
        else:
            self.logger.warning("spaCy not available. Using simple text processing.")
        
        self.logger.info("NLP Processor initialized")
    
    def is_available(self):
        """Check if spaCy is available"""
        return SPACY_AVAILABLE and self.nlp is not None
    
    def _load_model(self, model_name):
        """Load spaCy model"""
        try:
            self.nlp = spacy.load(model_name)
            self.logger.info(f"Loaded spaCy model: {model_name}")
        except OSError:
            self.logger.warning(f"Model {model_name} not found. Attempting to download...")
            try:
                import subprocess
                subprocess.run(["python", "-m", "spacy", "download", model_name], 
                             check=True)
                self.nlp = spacy.load(model_name)
                self.logger.info(f"Downloaded and loaded: {model_name}")
            except Exception as e:
                self.logger.error(f"Failed to download model: {e}")
                try:
                    self.nlp = spacy.blank("en")
                    self.logger.warning("Using blank English model as fallback")
                except:
                    self.logger.error("Could not create blank model either")
    
    def process(self, text):
        """
        Process text and return spaCy Doc object
        
        Args:
            text: Input text to process
            
        Returns:
            spaCy Doc object or None
        """
        if not self.nlp:
            return None
        
        return self.nlp(text)
    
    def tokenize(self, text):
        """
        Tokenize text
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        if not self.nlp:
            return text.split()
        
        doc = self.process(text)
        if doc:
            return [token.text for token in doc]
        return []
    
    def lemmatize(self, text):
        """
        Lemmatize text
        
        Args:
            text: Input text
            
        Returns:
            List of lemmas
        """
        if not self.nlp:
            return text.lower().split()
        
        doc = self.process(text)
        if doc:
            return [token.lemma_ for token in doc if not token.is_punct]
        return []
    
    def get_lemmas_with_pos(self, text):
        """
        Get lemmas with their POS tags
        
        Args:
            text: Input text
            
        Returns:
            List of tuples (lemma, POS)
        """
        if not self.nlp:
            return [(word, 'UNK') for word in text.split()]
        
        doc = self.process(text)
        if doc:
            return [(token.lemma_, token.pos_) for token in doc if not token.is_punct]
        return []
    
    def extract_entities(self, text):
        """
        Extract named entities from text
        
        Args:
            text: Input text
            
        Returns:
            List of tuples (entity_text, entity_label)
        """
        if not self.nlp:
            return []
        
        doc = self.process(text)
        if doc:
            return [(ent.text, ent.label_) for ent in doc.ents]
        return []
    
    def extract_dates(self, text):
        """
        Extract date entities from text
        
        Args:
            text: Input text
            
        Returns:
            List of date strings
        """
        entities = self.extract_entities(text)
        return [entity for entity, label in entities if label == 'DATE']
    
    def extract_persons(self, text):
        """
        Extract person entities from text
        
        Args:
            text: Input text
            
        Returns:
            List of person names
        """
        entities = self.extract_entities(text)
        return [entity for entity, label in entities if label == 'PERSON']
    
    def extract_organizations(self, text):
        """
        Extract organization entities from text
        
        Args:
            text: Input text
            
        Returns:
            List of organization names
        """
        entities = self.extract_entities(text)
        return [entity for entity, label in entities if label == 'ORG']
    
    def extract_locations(self, text):
        """
        Extract location entities from text
        
        Args:
            text: Input text
            
        Returns:
            List of location names
        """
        entities = self.extract_entities(text)
        locations = []
        for entity, label in entities:
            if label in ['GPE', 'LOC', 'FAC']:
                locations.append(entity)
        return locations
    
    def get_nouns(self, text):
        """
        Extract nouns from text
        
        Args:
            text: Input text
            
        Returns:
            List of nouns
        """
        if not self.nlp:
            return [word for word in text.split() if len(word) > 2]
        
        doc = self.process(text)
        if doc:
            return [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]
        return []
    
    def get_verbs(self, text):
        """
        Extract verbs from text
        
        Args:
            text: Input text
            
        Returns:
            List of verbs
        """
        if not self.nlp:
            return []
        
        doc = self.process(text)
        if doc:
            return [token.lemma_ for token in doc if token.pos_ == 'VERB']
        return []
    
    def get_adjectives(self, text):
        """
        Extract adjectives from text
        
        Args:
            text: Input text
            
        Returns:
            List of adjectives
        """
        if not self.nlp:
            return []
        
        doc = self.process(text)
        if doc:
            return [token.text for token in doc if token.pos_ == 'ADJ']
        return []
    
    def preprocess_for_ml(self, text):
        """
        Preprocess text for ML model
        
        Args:
            text: Input text
            
        Returns:
            Preprocessed text string
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Lemmatize
        lemmas = self.lemmatize(text)
        
        return ' '.join(lemmas)
    
    def get_sentence_structure(self, text):
        """
        Analyze sentence structure
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with sentence analysis
        """
        return {
            'num_tokens': len(text.split()),
            'has_question': '?' in text,
            'is_command': text.split()[0].lower() in ['open', 'close', 'create', 'delete', 'search', 'send', 'get', 'set'] if text else False,
        }
    
    def extract_action_words(self, text):
        """
        Extract action words (verbs) from text for intent detection
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of action categories
        """
        text_lower = text.lower()
        
        actions = {
            'create': [],
            'delete': [],
            'open': [],
            'search': [],
            'send': [],
            'get': [],
            'set': [],
            'other': []
        }
        
        action_verbs = {
            'create': ['create', 'make', 'add', 'new', 'generate'],
            'delete': ['delete', 'remove', 'erase', 'clear'],
            'open': ['open', 'launch', 'start', 'run', 'execute'],
            'search': ['search', 'find', 'look', 'seek'],
            'send': ['send', 'email', 'mail', 'share'],
            'get': ['get', 'show', 'display', 'tell', 'read'],
            'set': ['set', 'configure', 'change', 'update']
        }
        
        for action, keywords in action_verbs.items():
            for kw in keywords:
                if kw in text_lower:
                    actions[action].append(kw)
                    break
        
        return actions
    
    def extract_time_expressions(self, text):
        """
        Extract time expressions from text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of time expressions
        """
        time_patterns = {
            'today': r'\btoday\b',
            'tomorrow': r'\btomorrow\b',
            'this_week': r'\bthis week\b',
            'next_week': r'\bnext week\b',
            'minutes': r'\b(\d+)\s*minutes?\b',
            'hours': r'\b(\d+)\s*hours?\b',
            'days': r'\b(\d+)\s*days?\b',
        }
        
        times = {}
        text_lower = text.lower()
        
        for time_type, pattern in time_patterns.items():
            match = re.search(pattern, text_lower)
            if match:
                if time_type in ['minutes', 'hours', 'days']:
                    times[time_type] = int(match.group(1))
                else:
                    times[time_type] = True
        
        return times
    
    def simple_parse(self, text):
        """
        Simple pattern-based parsing for common commands
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with parsed information
        """
        text_lower = text.lower()
        
        parsed = {
            'action': None,
            'target': None,
            'location': None,
            'time': None,
            'modifier': None,
            'entities': []
        }
        
        # Extract action
        action_words = {
            'open': ['open', 'launch', 'start'],
            'close': ['close', 'stop', 'exit'],
            'create': ['create', 'make', 'new'],
            'delete': ['delete', 'remove'],
            'search': ['search', 'find', 'look'],
            'send': ['send', 'email'],
            'read': ['read', 'check', 'get'],
            'set': ['set', 'configure'],
        }
        
        for action, keywords in action_words.items():
            if any(kw in text_lower for kw in keywords):
                parsed['action'] = action
                break
        
        # Extract time
        parsed['time'] = self.extract_time_expressions(text)
        
        # Extract location (simple keyword matching)
        locations = ['new york', 'london', 'paris', 'tokyo', 'mumbai', 'delhi', 'bangalore']
        for loc in locations:
            if loc in text_lower:
                parsed['location'] = [loc.title()]
                break
        
        return parsed


# ============================================
# Main function for testing
# ============================================

def test_nlp_processor():
    """Test NLP processor"""
    print("Testing NLP Processor...")
    
    nlp = NLPProcessor()
    
    test_texts = [
        "Open Chrome browser",
        "What's the weather in New York tomorrow?",
        "Search for python tutorials",
        "Create a new file named report",
        "Set reminder for 3pm today",
    ]
    
    for text in test_texts:
        print(f"\n{'='*50}")
        print(f"Input: {text}")
        print(f"Tokens: {nlp.tokenize(text)}")
        print(f"Lemmas: {nlp.lemmatize(text)}")
        print(f"Action words: {nlp.extract_action_words(text)}")
        print(f"Simple parse: {nlp.simple_parse(text)}")
    
    return nlp


if __name__ == "__main__":
    test_nlp_processor()
