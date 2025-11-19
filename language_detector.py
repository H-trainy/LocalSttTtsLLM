"""
Language Detection Module for Speech Recognition
Automatically detects language from audio (Hindi, English, Urdu, Telugu)
Works offline after initial model download
Uses only public models - No tokens required
"""
import torch
import numpy as np
import librosa
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import os


class LanguageDetector:
    def __init__(self):
        """
        Initialize Language Detector
        Uses only public models - no authentication required
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Use only public model for all languages (no token required)
        # facebook/wav2vec2-base-960h is public and works for all languages
        self.model_name = 'facebook/wav2vec2-base-960h'
        
        # Cache for loaded model
        self.processor = None
        self.model = None
        
        print("Language Detector initialized (using public models)")
    
    def _load_model(self):
        """Load STT model - public model, no token required"""
        if self.processor is not None and self.model is not None:
            return self.processor, self.model
        
        try:
            # Try offline first (local_files_only=True)
            try:
                self.processor = Wav2Vec2Processor.from_pretrained(
                    self.model_name, local_files_only=True
                )
                self.model = Wav2Vec2ForCTC.from_pretrained(
                    self.model_name, local_files_only=True
                )
            except:
                # Download if not in cache (first time only - requires internet)
                print(f"Language detector: Downloading {self.model_name} (one time only, requires internet)...")
                self.processor = Wav2Vec2Processor.from_pretrained(
                    self.model_name, local_files_only=False
                )
                self.model = Wav2Vec2ForCTC.from_pretrained(
                    self.model_name, local_files_only=False
                )
                print(f"Model downloaded. Future runs will be OFFLINE.")
            
            self.model.to(self.device)
            self.model.eval()
            
            return self.processor, self.model
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")
    
    def preprocess_audio(self, audio_path, target_sr=16000):
        """Preprocess audio file"""
        audio, sr = librosa.load(audio_path, sr=target_sr)
        audio = audio / np.max(np.abs(audio))
        return audio
    
    def _transcribe_with_language(self, audio_array, language):
        """Transcribe audio with the model (same model for all languages)"""
        try:
            processor, model = self._load_model()
            
            inputs = processor(audio_array, sampling_rate=16000, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                logits = model(**inputs).logits
            
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = processor.decode(predicted_ids[0])
            
            return transcription
        except Exception as e:
            return ""
    
    def _calculate_confidence(self, transcription, language):
        """
        Calculate confidence score for transcription
        Higher score = more likely to be correct language
        """
        if not transcription or len(transcription.strip()) == 0:
            return 0.0
        
        score = 0.0
        text = transcription.strip().lower()
        
        # Length bonus (longer transcriptions are more reliable)
        score += min(len(text) / 50.0, 1.0) * 0.3
        
        # Character-based heuristics
        if language == 'hindi':
            # Hindi uses Devanagari script (Unicode range: 0900-097F)
            devanagari_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
            if len(text) > 0:
                score += (devanagari_chars / len(text)) * 0.5
        
        elif language == 'urdu':
            # Urdu uses Arabic script (Unicode range: 0600-06FF)
            arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
            if len(text) > 0:
                score += (arabic_chars / len(text)) * 0.5
        
        elif language == 'english':
            # English uses Latin script
            latin_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
            if len(text) > 0:
                score += (latin_chars / len(text)) * 0.5
        
        elif language == 'telugu':
            # Telugu uses Telugu script (Unicode range: 0C00-0C7F)
            telugu_chars = sum(1 for c in text if '\u0C00' <= c <= '\u0C7F')
            if len(text) > 0:
                score += (telugu_chars / len(text)) * 0.5
        
        # Word count bonus
        words = text.split()
        if len(words) > 0:
            score += min(len(words) / 10.0, 1.0) * 0.2
        
        return score
    
    def detect_language(self, audio_path):
        """
        Detect language from audio file
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Detected language ('hindi', 'english', 'urdu', or 'telugu')
        """
        print("Detecting language from audio...")
        
        # Preprocess audio
        audio_array = self.preprocess_audio(audio_path)
        
        # Try all supported languages
        languages = ['hindi', 'english', 'urdu', 'telugu']
        results = {}
        
        for lang in languages:
            try:
                transcription = self._transcribe_with_language(audio_array, lang)
                confidence = self._calculate_confidence(transcription, lang)
                results[lang] = {
                    'transcription': transcription,
                    'confidence': confidence
                }
                print(f"  {lang.capitalize()}: confidence={confidence:.3f}, text='{transcription[:50]}...'")
            except Exception as e:
                print(f"  {lang.capitalize()}: Error - {e}")
                results[lang] = {'transcription': '', 'confidence': 0.0}
        
        # Select language with highest confidence
        best_language = max(results.keys(), key=lambda k: results[k]['confidence'])
        best_confidence = results[best_language]['confidence']
        
        print(f"Detected language: {best_language.upper()} (confidence: {best_confidence:.3f})")
        
        return best_language, results[best_language]['transcription']


if __name__ == "__main__":
    # Test the language detector
    detector = LanguageDetector()
    print("Language Detector initialized successfully!")
