"""
Voice recording module for capturing audio input with RNNoise/WebRTC noise reduction
"""
import pyaudio
import wave
import os
from noise_reduction import NoiseReducer


class VoiceRecorder:
    def __init__(self, sample_rate=16000, channels=1, chunk=1024, format=pyaudio.paInt16):
        """
        Initialize voice recorder
        
        Args:
            sample_rate: Audio sample rate (default: 16000)
            channels: Number of audio channels (default: 1 for mono)
            chunk: Buffer size (default: 1024)
            format: Audio format (default: pyaudio.paInt16)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk = chunk
        self.format = format
        self.audio = pyaudio.PyAudio()
        
        # Initialize noise reducer (RNNoise/WebRTC)
        self.noise_reducer = NoiseReducer()
    
    def record(self, duration=5, output_path="input.wav"):
        """
        Record audio for specified duration
        
        Args:
            duration: Recording duration in seconds (default: 5)
            output_path: Path to save recorded audio
        
        Returns:
            Path to saved audio file
        """
        print(f"Recording for {duration} seconds... Speak now!")
        
        # Open audio stream
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        frames = []
        
        # Record audio
        for _ in range(0, int(self.sample_rate / self.chunk * duration)):
            data = stream.read(self.chunk)
            frames.append(data)
        
        print("Recording finished!")
        
        # Stop and close stream
        stream.stop_stream()
        stream.close()
        
        # Save audio file
        wf = wave.open(output_path, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.format))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # Apply noise reduction using RNNoise/WebRTC
        output_path = self.noise_reducer.reduce_noise(output_path)
        
        return output_path
    
    def record_until_silence(self, silence_threshold=500, silence_duration=5, output_path="input.wav"):
        """
        Record audio until silence is detected
        
        Args:
            silence_threshold: Threshold for silence detection
            silence_duration: Duration of silence before stopping (seconds)
            output_path: Path to save recorded audio
        
        Returns:
            Path to saved audio file
        """
        import struct
        
        print(f"Recording... Speak now. Recording will stop after {silence_duration} seconds of silence.")
        
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        frames = []
        silent_chunks = 0
        silent_chunks_threshold = int(self.sample_rate / self.chunk * silence_duration)
        
        while True:
            data = stream.read(self.chunk)
            frames.append(data)
            
            # Check for silence
            audio_data = struct.unpack(f"{self.chunk * self.channels}h", data)
            max_amplitude = max(audio_data)
            
            if max_amplitude < silence_threshold:
                silent_chunks += 1
                if silent_chunks > silent_chunks_threshold:
                    break
            else:
                silent_chunks = 0
        
        print("Recording finished!")
        
        stream.stop_stream()
        stream.close()
        
        # Save audio file
        wf = wave.open(output_path, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.format))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # Apply noise reduction using RNNoise/WebRTC
        output_path = self.noise_reducer.reduce_noise(output_path)
        
        return output_path
    
    
    def cleanup(self):
        """Clean up audio resources"""
        self.audio.terminate()


if __name__ == "__main__":
    # Test the voice recorder
    recorder = VoiceRecorder()
    print("Voice recorder initialized successfully!")
    recorder.cleanup()

