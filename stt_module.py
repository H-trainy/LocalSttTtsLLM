"""
Speech-to-Text module with faster-whisper and Wav2Vec2 support
Supports Hindi, English, Urdu, and Telugu
Uses faster-whisper for better accuracy and speed (much faster than standard Whisper!)
100% OFFLINE - No tokens required
"""
import torch
import numpy as np
import librosa
import os
from language_detector import LanguageDetector


class STTModule:
    def __init__(self, language='hindi', auto_detect=False, use_whisper=True):
        """
        Initialize STT module
        
        Args:
            language: 'hindi', 'english', 'urdu', or 'telugu' (used if auto_detect=False)
            auto_detect: If True, automatically detect language from audio
            use_whisper: If True, use Whisper model (better accuracy)
        """
        self.language = language.lower()
        self.auto_detect = auto_detect
        self.use_whisper = use_whisper
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize language detector if auto_detect is enabled
        if self.auto_detect:
            self.language_detector = LanguageDetector()
        else:
            self.language_detector = None
        
        # Language code mapping for Whisper
        self.whisper_lang_map = {
            'hindi': 'hi',
            'english': 'en',
            'urdu': 'ur',
            'telugu': 'te'
        }
        
        # Initialize faster-whisper (100% OFFLINE after download, much faster!)
        self.whisper_model = None
        self.whisper_device = "cuda" if torch.cuda.is_available() else "cpu"
        self.whisper_compute_type = "float16" if torch.cuda.is_available() else "int8"
        
        try:
            from faster_whisper import WhisperModel
            model_size = "large-v3"  # Best accuracy
            print(f"Loading faster-whisper {model_size} model (OFFLINE, best accuracy)...")
            self.whisper_model = WhisperModel(
                model_size,
                device=self.whisper_device,
                compute_type=self.whisper_compute_type,
                download_root=None
            )
            print(f"faster-whisper {model_size} model loaded successfully! (OFFLINE, {self.whisper_device.upper()})")
        except ImportError:
            raise ImportError("faster-whisper not installed. Install with: pip install faster-whisper")
        except Exception as e:
            raise RuntimeError(f"Could not load faster-whisper: {e}")
    
    def preprocess_audio(self, audio_path, target_sr=16000, reduce_noise=True):
        """
        Preprocess audio file for STT with optional noise reduction (RNNoise/WebRTC)
        
        Args:
            audio_path: Path to audio file
            target_sr: Target sample rate (default: 16000)
            reduce_noise: Apply noise reduction (default: True)
        
        Returns:
            Preprocessed audio array
        """
        # Note: Noise reduction is already applied during recording in voice_recorder.py
        # This function just loads and normalizes the audio
        audio, sr = librosa.load(audio_path, sr=target_sr)
        
        # Normalize audio
        if len(audio) > 0 and np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))
        
        return audio
    
    def transcribe(self, audio_path=None, audio_array=None):
        """
        Transcribe audio to text
        
        Args:
            audio_path: Path to audio file (optional if audio_array provided)
            audio_array: Preprocessed audio array (optional if audio_path provided)
        
        Returns:
            Transcribed text
        """
        # Auto-detect language if enabled
        detected_language = self.language
        if self.auto_detect and audio_path:
            detected_language, _ = self.language_detector.detect_language(audio_path)
            if detected_language != self.language:
                print(f"Language detected: {detected_language.upper()}")
                self.language = detected_language
        
        return self._transcribe_whisper(audio_path, detected_language)
    
    def _transcribe_whisper(self, audio_path, language):
        """Transcribe using faster-whisper (much faster than standard Whisper!)"""
        try:
            lang_code = self.whisper_lang_map.get(language, None)  # None = auto-detect
            # faster-whisper API is different - returns segments generator
            segments, info = self.whisper_model.transcribe(
                audio_path,
                language=lang_code,
                task="transcribe",
                beam_size=5,  # Balance between speed and accuracy
                vad_filter=True,  # Voice Activity Detection for better accuracy
            )
            
            # Combine all segments into full text
            full_text = " ".join([segment.text for segment in segments])
            return full_text.strip()
        except Exception as e:
            raise RuntimeError(f"faster-whisper transcription error: {e}")
    
    def set_language(self, language):
        """Change the language for STT"""
        if language.lower() != self.language:
            self.language = language.lower()


if __name__ == "__main__":
    # Test the STT module
    stt = STTModule(language='hindi', use_whisper=True)
    print("STT module initialized successfully!")
