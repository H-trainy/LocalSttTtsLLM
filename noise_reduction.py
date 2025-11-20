"""
Offline Noise Reduction using WebRTC
Provides real-time noise cancellation for clear audio
"""
import os
import numpy as np
import soundfile as sf


class NoiseReducer:
    def __init__(self):
        """Initialize noise reduction with WebRTC"""
        self.webrtc_available = False
        self._init_webrtc()
        
        if not self.webrtc_available:
            print("[WARNING] No noise reduction available. Install webrtcvad: pip install webrtcvad")
        else:
            print("[INFO] WebRTC VAD and noise suppression ready")
    
    def _init_webrtc(self):
        """Initialize WebRTC VAD and Noise Suppression"""
        try:
            import webrtcvad
            self.webrtc_available = True
            self.webrtc_vad = webrtcvad.Vad(2)  # Aggressiveness: 0-3, 2 is balanced
        except ImportError:
            self.webrtc_available = False
    
    def reduce_noise_webrtc(self, audio_path, output_path=None):
        """
        Apply WebRTC noise suppression and VAD
        
        Args:
            audio_path: Input audio file path
            output_path: Output audio file path (if None, overwrites input)
        
        Returns:
            Path to processed audio file
        """
        if not self.webrtc_available:
            return audio_path
        
        if output_path is None:
            output_path = audio_path
        
        try:
            import webrtcvad
            
            # Load audio
            audio, sr = sf.read(audio_path)
            
            # Convert to mono if stereo
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)
            
            # WebRTC VAD requires 16kHz, 16-bit PCM, mono
            if sr != 16000:
                import librosa
                audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
                sr = 16000
            
            # Convert to int16 PCM
            audio_int16 = (audio * 32767).astype(np.int16)
            
            # Apply VAD (Voice Activity Detection) - removes silence
            print("[AUDIO] Applying WebRTC VAD (removing silence)...")
            frame_duration_ms = 30  # 10, 20, or 30 ms frames (WebRTC requirement)
            frame_size = int(sr * frame_duration_ms / 1000)
            # Ensure frame size is even (required by WebRTC)
            frame_size = (frame_size // 2) * 2
            
            vad = webrtcvad.Vad(2)  # Aggressiveness: 0-3, 2 is balanced
            frames = []
            
            # Process audio in frames
            for i in range(0, len(audio_int16) - frame_size, frame_size):
                frame = audio_int16[i:i + frame_size]
                
                # Ensure frame is exactly the right size
                if len(frame) == frame_size:
                    frame_bytes = frame.tobytes()
                    
                    # Check if frame contains speech
                    try:
                        if vad.is_speech(frame_bytes, sr):
                            frames.append(frame)
                    except Exception as e:
                        # If VAD fails, include frame anyway
                        frames.append(frame)
            
            if len(frames) == 0:
                print("[WARNING] No speech detected after VAD")
                return audio_path
            
            # Combine frames
            audio_processed = np.concatenate(frames)
            
            # Apply noise suppression using spectral subtraction
            print("[AUDIO] Applying spectral noise suppression...")
            audio_processed = self._spectral_subtraction(audio_processed.astype(np.float32) / 32767.0, sr)
            
            # Normalize
            if len(audio_processed) > 0 and np.max(np.abs(audio_processed)) > 0:
                audio_processed = audio_processed / np.max(np.abs(audio_processed))
            
            # Save processed audio
            sf.write(output_path, audio_processed, sr)
            print("[AUDIO] WebRTC noise reduction applied successfully")
            
        except Exception as e:
            print(f"[WARNING] WebRTC processing failed: {e}")
            return audio_path
        
        return output_path
    
    def _spectral_subtraction(self, audio, sr, alpha=2.0, beta=0.01):
        """
        Simple spectral subtraction for noise reduction (fallback method)
        
        Args:
            audio: Audio array
            sr: Sample rate
            alpha: Over-subtraction factor
            beta: Spectral floor factor
        
        Returns:
            Noise-reduced audio
        """
        try:
            import librosa
            import scipy.signal
            
            # Compute STFT
            stft = librosa.stft(audio, n_fft=2048, hop_length=512)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise from first 0.5 seconds (assuming it's mostly noise)
            noise_frames = int(0.5 * sr / 512)
            if noise_frames > 0 and noise_frames < magnitude.shape[1]:
                noise_spectrum = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)
            else:
                noise_spectrum = np.mean(magnitude, axis=1, keepdims=True) * 0.1
            
            # Spectral subtraction
            magnitude_clean = magnitude - alpha * noise_spectrum
            magnitude_clean = np.maximum(magnitude_clean, beta * magnitude)
            
            # Reconstruct audio
            stft_clean = magnitude_clean * np.exp(1j * phase)
            audio_clean = librosa.istft(stft_clean, hop_length=512)
            
            return audio_clean
        except Exception as e:
            print(f"[WARNING] Spectral subtraction failed: {e}")
            return audio
    
    def reduce_noise(self, audio_path, output_path=None):
        """
        Apply noise reduction using WebRTC
        
        Args:
            audio_path: Input audio file path
            output_path: Output audio file path (if None, overwrites input)
        
        Returns:
            Path to processed audio file
        """
        if self.webrtc_available:
            return self.reduce_noise_webrtc(audio_path, output_path)
        return audio_path


if __name__ == "__main__":
    reducer = NoiseReducer()
    print(f"WebRTC available: {reducer.webrtc_available}")

