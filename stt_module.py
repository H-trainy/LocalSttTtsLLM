"""
Speech-to-Text module with Whisper and Wav2Vec2 support
Supports Hindi, English, Urdu, and Telugu
Uses Whisper for better accuracy after language detection
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
        
        # Initialize Whisper if requested (100% OFFLINE after download)
        self.whisper_model = None
        if self.use_whisper:
            try:
                import whisper
                # Load base Whisper model (works 100% offline after initial download)
                print("Loading Whisper model (OFFLINE)...")
                self.whisper_model = whisper.load_model("base", download_root=None)
                print("Whisper model loaded successfully! (OFFLINE)")
            except ImportError:
                print("Warning: Whisper not installed. Install with: pip install openai-whisper")
                print("Falling back to Wav2Vec2 models...")
                self.use_whisper = False
            except Exception as e:
                print(f"Warning: Could not load Whisper: {e}")
                print("Falling back to Wav2Vec2 models...")
                self.use_whisper = False
        
        # Wav2Vec2 models as fallback (using only public models - no token required)
        if not self.use_whisper:
            self._init_wav2vec2_models()
        else:
            # Don't load Wav2Vec2 if Whisper is available
            self.processor = None
            self.model = None
    
    def _init_wav2vec2_models(self):
        """Initialize Wav2Vec2 models - using only public models (no token required)"""
        from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
        
        # Use only public models - no authentication required
        # facebook/wav2vec2-base-960h is public and works for all languages
        self.model_name = 'facebook/wav2vec2-base-960h'
        
        # Load model for current language
        if not self.auto_detect:
            self._load_wav2vec2_model()
    
    def _load_wav2vec2_model(self):
        """Load Wav2Vec2 model - public model, no token required"""
        from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
        
        try:
            # Try offline first (local_files_only=True)
            try:
                self.processor = Wav2Vec2Processor.from_pretrained(
                    self.model_name, local_files_only=True
                )
                self.model = Wav2Vec2ForCTC.from_pretrained(
                    self.model_name, local_files_only=True
                )
                print(f"Loaded {self.model_name} from cache (OFFLINE)")
            except:
                # Only download if not in cache (first time only)
                print(f"Model not in cache. Downloading {self.model_name} (requires internet - one time only)...")
                self.processor = Wav2Vec2Processor.from_pretrained(
                    self.model_name, local_files_only=False
                )
                self.model = Wav2Vec2ForCTC.from_pretrained(
                    self.model_name, local_files_only=False
                )
                print(f"Model downloaded. Future runs will be OFFLINE.")
            
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            raise RuntimeError(f"Failed to load STT model: {e}")
    
    def preprocess_audio(self, audio_path, target_sr=16000):
        """Preprocess audio file for STT"""
        audio, sr = librosa.load(audio_path, sr=target_sr)
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
        
        # Use Whisper if available
        if self.use_whisper and self.whisper_model:
            return self._transcribe_whisper(audio_path, detected_language)
        else:
            # Use Wav2Vec2
            return self._transcribe_wav2vec2(audio_path, audio_array)
    
    def _transcribe_whisper(self, audio_path, language):
        """Transcribe using Whisper"""
        try:
            lang_code = self.whisper_lang_map.get(language, 'en')
            result = self.whisper_model.transcribe(
                audio_path,
                language=lang_code,
                task="transcribe"
            )
            return result["text"].strip()
        except Exception as e:
            print(f"Whisper transcription error: {e}, trying Wav2Vec2...")
            # Fallback to Wav2Vec2
            if not hasattr(self, 'model') or self.model is None:
                self._init_wav2vec2_models()
                self._load_wav2vec2_model()
            return self._transcribe_wav2vec2(audio_path, None)
    
    def _transcribe_wav2vec2(self, audio_path, audio_array):
        """Transcribe using Wav2Vec2"""
        from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
        
        # Load model if not loaded
        if not hasattr(self, 'model') or self.model is None:
            self._load_wav2vec2_model()
        
        if audio_array is None:
            if audio_path is None:
                raise ValueError("Either audio_path or audio_array must be provided")
            audio_array = self.preprocess_audio(audio_path)
        
        # Process audio
        inputs = self.processor(audio_array, sampling_rate=16000, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get predictions
        with torch.no_grad():
            logits = self.model(**inputs).logits
        
        # Decode
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = self.processor.decode(predicted_ids[0])
        
        return transcription
    
    def set_language(self, language):
        """Change the language for STT"""
        if language.lower() != self.language:
            self.language = language.lower()
            if not self.use_whisper:
                self._load_wav2vec2_model()


if __name__ == "__main__":
    # Test the STT module
    stt = STTModule(language='hindi', use_whisper=True)
    print("STT module initialized successfully!")
