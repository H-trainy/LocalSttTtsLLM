"""
Speech-to-Text module using faster-whisper LARGE-V3
✔ Supports MIXED languages in one audio (Hindi + English + Telugu + Urdu)
✔ Uses Whisper auto-language detection
✔ 100% OFFLINE after first download
✔ Clean, fast, and stable
"""

import numpy as np
import librosa
import torch


class STTModule:
    def __init__(self, use_whisper=True):
        """
        Initialize STT Module (Multilingual Version)

        Args:
            use_whisper: Always True (Whisper has best multilingual accuracy)
        """
        self.use_whisper = use_whisper
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load faster-whisper LARGE-V3
        try:
            from faster_whisper import WhisperModel
            print("Loading faster-whisper large-v3 (best multilingual accuracy)...")

            self.model = WhisperModel(
                "large-v3",
                device=self.device,
                compute_type="float16" if self.device == "cuda" else "int8",
            )

            print(f"Whisper LARGE-V3 loaded successfully on {self.device.upper()}!")

        except ImportError:
            raise ImportError("Install faster-whisper: pip install faster-whisper")
        except Exception as e:
            raise RuntimeError(f"Failed to load faster-whisper: {e}")

    def preprocess_audio(self, audio_path, target_sr=16000):
        """
        Load + normalize audio
        Speech recording already has noise reduction applied, so only normalization is needed
        """
        audio, sr = librosa.load(audio_path, sr=target_sr)

        # Normalize audio volume
        if len(audio) > 0 and np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))

        return audio

    def transcribe(self, audio_path):
        """
        Transcribe audio using multilingual Whisper (mixed language capable)

        Args:
            audio_path: path to WAV/MP3/M4A file

        Returns:
            full_text: Transcribed text (may contain Hindi + English + Telugu)
        """

        print("Transcribing with multi-language Whisper...")

        try:
            # DO NOT set language → Whisper auto-detects (supports mixed speech!)
            segments, info = self.model.transcribe(
                audio_path,
                language=None,            # <– enables multi-language detection
                task="transcribe",        # <– transcription, NOT translation
                beam_size=5,
                vad_filter=True,
            )

            # Merge all segments into final text
            full_text = " ".join([seg.text for seg in segments])
            full_text = full_text.strip()

            if full_text == "":
                print("[STT] No speech detected.")
                return ""

            print("[STT] Transcription complete.")
            return full_text

        except Exception as e:
            raise RuntimeError(f"Whisper transcription error: {e}")

