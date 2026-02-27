"""Core package for Secure Intelligent Desktop Assistant"""
from .voice import VoiceEngine
from .face_auth import FaceAuthenticator
from .nlp_processor import NLPProcessor

__all__ = ['VoiceEngine', 'FaceAuthenticator', 'NLPProcessor']
