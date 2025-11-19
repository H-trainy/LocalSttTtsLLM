import os
import subprocess
import sys
import tempfile
import wave


class TTSModule:
    def __init__(self, language='hindi'):
        """
        Initialize TTS module - OFFLINE ONLY
        
        Args:
            language: 'hindi', 'english', 'urdu', or 'telugu'
        """
        self.language = language.lower()
        print(f"Initializing OFFLINE TTS module for {self.language}...")
        
        # Language keywords for voice matching
        self.language_keywords = {
            'hindi': ['hindi', 'hi-in', 'hin', 'hindustani', 'hi_in', 'hiin', 'hindi desktop', 'microsoft hindi'],
            'english': ['english', 'en-us', 'en-gb', 'en-in', 'eng'],
            'urdu': ['urdu', 'ur-pk', 'ur', 'urd'],
            'telugu': ['telugu', 'te-in', 'tel', 'telu', 'te']
        }
        
        # Try offline TTS methods in order of preference
        self.tts_method = None
        self.current_voice = None
        self.piper_available = False
        self.piper_model_path = None
        
        # Method 1: Try Piper TTS (neural TTS - completely offline, best for Hindi)
        self._init_piper()
        
        # Method 2: Try pyttsx3 (system TTS - completely offline)
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 1.0)
            
            # Try to select appropriate voice for language
            self._select_voice_for_language()
            
            self.pyttsx3_available = True
            # Only set as primary if Piper is not available or not for Hindi
            if not self.piper_available or self.language != 'hindi':
                self.tts_method = 'pyttsx3'
            if self.current_voice:
                print(f"Using pyttsx3 (OFFLINE) with voice: {self.current_voice}")
            else:
                print("Using pyttsx3 (OFFLINE) with default voice")
        except Exception as e:
            self.pyttsx3_available = False
            print(f"Warning: pyttsx3 not available: {e}")
        
        # Method 3: PowerShell TTS (Windows only - completely offline)
        if sys.platform == 'win32':
            self.powershell_available = True
            if not self.tts_method:
                self.tts_method = 'powershell'
                print("Using PowerShell TTS (OFFLINE) for text-to-speech")
        else:
            self.powershell_available = False
        
        if not self.tts_method:
            raise RuntimeError("No offline TTS method available. Install: pip install pyttsx3")
    
    def _init_piper(self):
        """Initialize Piper TTS (offline neural TTS - best for Hindi)"""
        # Only use Piper for Hindi (it's optimized for Hindi)
        # For other languages, use pyttsx3/PowerShell which work better
        if self.language != 'hindi':
            self.piper_available = False
            return
        
        # Check if piper command is available
        try:
            result = subprocess.run(['piper', '--version'], capture_output=True, timeout=2, text=True)
            if result.returncode == 0:
                self.piper_available = True
                # Don't set as primary method yet - will be used only if model exists
                
                # Piper model for Hindi
                self.piper_model = 'hi_IN/arya/medium'
                print(f"Piper TTS available for Hindi")
                print(f"Model: {self.piper_model}")
                print("Note: Download Hindi model with: piper download --language hi_IN --output-dir piper_models")
                return
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # Piper not installed - that's okay, will use fallback
            pass
        except Exception as e:
            # Piper error - that's okay, will use fallback
            pass
        
        # Piper not available - will use pyttsx3/PowerShell instead
        self.piper_available = False
    
    def _select_voice_for_language(self):
        """Select the best voice for the current language"""
        try:
            voices = self.engine.getProperty('voices')
            if not voices:
                return
            
            keywords = self.language_keywords.get(self.language, [self.language])
            
            # First, try exact matches
            for voice in voices:
                voice_name_lower = voice.name.lower()
                voice_id_lower = voice.id.lower()
                
                for keyword in keywords:
                    if keyword in voice_name_lower or keyword in voice_id_lower:
                        self.engine.setProperty('voice', voice.id)
                        self.current_voice = voice.name
                        return
            
            # If no match found, list available voices for debugging
            print(f"\n[DEBUG] No exact match found for {self.language}. Available voices:")
            for i, voice in enumerate(voices):
                print(f"  {i+1}. {voice.name} (ID: {voice.id})")
            
            # Try to use any Indian language voice as fallback
            if self.language in ['hindi', 'telugu', 'urdu']:
                for voice in voices:
                    voice_name_lower = voice.name.lower()
                    voice_id_lower = voice.id.lower()
                    # More comprehensive Indian language detection
                    if any(indian in voice_name_lower or indian in voice_id_lower 
                           for indian in ['india', 'indian', 'in-', 'hi-', 'te-', 'ur-', 'hi_in', 'hiin']):
                        self.engine.setProperty('voice', voice.id)
                        self.current_voice = voice.name
                        print(f"[TTS] Using fallback voice: {voice.name}")
                        return
            
            # For English: use any English voice as fallback
            if self.language == 'english':
                for voice in voices:
                    voice_name_lower = voice.name.lower()
                    voice_id_lower = voice.id.lower()
                    if any(eng in voice_name_lower or eng in voice_id_lower 
                           for eng in ['english', 'en-', 'us', 'uk', 'gb']):
                        self.engine.setProperty('voice', voice.id)
                        self.current_voice = voice.name
                        print(f"[TTS] Using English fallback voice: {voice.name}")
                        return
            
            # Last resort: use first available voice and warn user
            if voices:
                self.engine.setProperty('voice', voices[0].id)
                self.current_voice = voices[0].name
                print(f"[WARNING] No {self.language} voice found. Using default voice: {voices[0].name}")
                print(f"[WARNING] Install {self.language} language pack in Windows Settings > Language")
        except Exception as e:
            print(f"Warning: Could not select voice: {e}")
            self.current_voice = None
    
    def speak(self, text):
        """
        Speak text directly using offline methods only
        
        Args:
            text: Text to convert to speech
        """
        if not text or not text.strip():
            return
        
        # Clean text
        text = text.strip()
        
        # Try methods in order
        # For Hindi: Try Piper first, then fallback to pyttsx3/PowerShell
        # For other languages: Use pyttsx3/PowerShell (they work better)
        if self.language == 'hindi' and self.piper_available:
            # Try Piper for Hindi, but fallback if it fails
            try:
                self._speak_piper(text)
                return
            except Exception as e:
                print(f"[TTS] Piper failed: {e}, using fallback...")
        
        # Use pyttsx3 or PowerShell for all languages (including Hindi fallback)
        if self.pyttsx3_available:
            self._speak_pyttsx3(text)
        elif self.powershell_available:
            self._speak_powershell(text)
        else:
            print(f"[WARNING] Could not speak text. No offline TTS method available.")
    
    def _speak_piper(self, text):
        """Speak using Piper TTS (offline neural TTS - best quality for Hindi)"""
        try:
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                wav_path = tmp_file.name
            
            # Find model file
            model_paths = [
                os.path.join('piper_models', self.piper_model, 'model.onnx'),
                os.path.join(os.path.expanduser('~'), '.local', 'share', 'piper', 'voices', self.piper_model, 'model.onnx'),
                os.path.join(os.path.expanduser('~'), 'piper', 'voices', self.piper_model, 'model.onnx'),
            ]
            
            model_file = None
            for path in model_paths:
                if os.path.exists(path):
                    model_file = path
                    break
            
            if not model_file:
                # Try using model name directly (piper will download if needed)
                model_file = self.piper_model
            
            # Use piper command to generate speech
            cmd = ['piper', '--model', model_file, '--output_file', wav_path]
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=text)
            
            if process.returncode == 0 and os.path.exists(wav_path):
                # Play the audio file using pydub (cross-platform)
                try:
                    from pydub import AudioSegment
                    from pydub.playback import play
                    audio = AudioSegment.from_wav(wav_path)
                    play(audio)
                except ImportError:
                    # Fallback to system player
                    if sys.platform == 'win32':
                        os.system(f'start "" "{wav_path}"')
                    elif sys.platform == 'darwin':
                        os.system(f'afplay "{wav_path}"')
                    else:
                        os.system(f'aplay "{wav_path}" 2>/dev/null || paplay "{wav_path}" 2>/dev/null')
                
                # Clean up
                import time
                time.sleep(0.5)
                try:
                    os.remove(wav_path)
                except:
                    pass
                print("[TTS] Speech completed (Piper)")
                return
            else:
                raise Exception(f"Piper failed: {stderr}")
        except Exception as e:
            print(f"[ERROR] Piper TTS error: {e}")
            print("[TTS] Falling back to other TTS methods...")
            # Fallback to other methods
            if self.pyttsx3_available:
                self._speak_pyttsx3(text)
            elif self.powershell_available:
                self._speak_powershell(text)
    
    def _speak_pyttsx3(self, text):
        """Speak using pyttsx3 (offline)"""
        try:
            # Ensure voice is set before speaking
            if self.language and not self.current_voice:
                self._select_voice_for_language()
            
            # Verify voice is set and show current voice
            current_voice_id = self.engine.getProperty('voice')
            current_voice_name = self.current_voice
            
            # Get voice name from ID if not already stored
            if not current_voice_name and current_voice_id:
                try:
                    voices = self.engine.getProperty('voices')
                    if voices:
                        for v in voices:
                            if v.id == current_voice_id:
                                current_voice_name = v.name
                                self.current_voice = v.name
                                break
                except:
                    pass
            
            print(f"[TTS] Speaking in {self.language.upper()}")
            if current_voice_name:
                print(f"[TTS] Using voice: {current_voice_name}")
            else:
                print(f"[TTS] Using default voice")
            
            # Ensure volume is set
            self.engine.setProperty('volume', 1.0)
            self.engine.setProperty('rate', 150)
            
            # Speak the text
            self.engine.say(text)
            self.engine.runAndWait()
            print("[TTS] Speech completed")
        except Exception as e:
            print(f"[ERROR] pyttsx3 error: {e}")
            print(f"[ERROR] Trying PowerShell fallback...")
            if self.powershell_available:
                self._speak_powershell(text)
            else:
                print(f"[ERROR] All offline TTS methods failed. Text was: {text[:50]}...")

    def _speak_powershell(self, text):
        """Speak using PowerShell (Windows - offline)"""
        try:
            # Escape text for PowerShell
            escaped_text = (text
                           .replace('\\', '\\\\')
                           .replace('"', '`"')
                           .replace('$', '`$')
                           .replace("'", "''")
                           .replace('\n', ' ')
                           .replace('\r', ' '))
            
            # Build keywords for voice matching
            keywords = self.language_keywords.get(self.language, [self.language])
            keywords_str = '", "'.join(keywords)
            
            ps_command = f'''
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Speech
$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speak.Volume = 100
$speak.Rate = 0

# Try to select appropriate voice for language
$voices = $speak.GetInstalledVoices()
$keywords = @("{keywords_str}")
$selected = $false

foreach ($voice in $voices) {{
    $voiceName = $voice.VoiceInfo.Name
    $voiceNameLower = $voiceName.ToLower()
    
    foreach ($keyword in $keywords) {{
        if ($voiceNameLower -like "*$keyword*") {{
            try {{
                $speak.SelectVoice($voiceName)
                Write-Host "[TTS] Selected voice: $voiceName"
                $selected = $true
                break
            }} catch {{
                # Continue searching
            }}
        }}
    }}
    if ($selected) {{ break }}
}}

# Fallback: Try Indian language voices for Hindi/Telugu/Urdu
if (-not $selected -and ("{self.language}" -in @("hindi", "telugu", "urdu"))) {{
    foreach ($voice in $voices) {{
        $voiceName = $voice.VoiceInfo.Name
        $voiceNameLower = $voiceName.ToLower()
        if ($voiceNameLower -like "*india*" -or $voiceNameLower -like "*indian*" -or 
            $voiceNameLower -like "*te-*" -or $voiceNameLower -like "*hi-*" -or 
            $voiceNameLower -like "*ur-*" -or $voiceNameLower -like "*in-*") {{
            try {{
                $speak.SelectVoice($voiceName)
                Write-Host "[TTS] Using fallback voice: $voiceName"
                $selected = $true
                break
            }} catch {{
                # Continue
            }}
        }}
    }}
}}

$speak.Speak("{escaped_text}")
'''
            result = subprocess.run(
                ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_command],
                timeout=60,
                text=True,
                capture_output=True
            )
            if result.returncode != 0:
                print(f"PowerShell TTS warning: {result.stderr}")
            if result.stdout:
                print(result.stdout.strip())
        except Exception as e:
            print(f"PowerShell TTS error: {e}")
            print(f"[ERROR] All offline TTS methods failed. Text was: {text[:50]}...")

    def synthesize(self, text, output_path="output.wav"):
        """Synthesize speech and save to file (offline)"""
        try:
            if self.pyttsx3_available:
                output_dir = os.path.dirname(output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                
                self.engine.save_to_file(text, output_path)
                self.engine.runAndWait()
                
                import time
                time.sleep(1)
                return output_path
            else:
                # Can't save with PowerShell, just speak
                self.speak(text)
            return output_path
        except Exception as e:
            print(f"Error synthesizing text: {e}")
            self.speak(text)  # Fallback to direct speech
            return output_path
    
    def set_language(self, language):
        """Change the language for TTS"""
        if language.lower() != self.language:
            self.language = language.lower()
            self.current_voice = None
            
            # Re-initialize Piper if switching to/from Hindi
            if self.language == 'hindi':
                self._init_piper()
            else:
                self.piper_available = False
            
            # Try to select appropriate voice
            if hasattr(self, 'engine') and self.pyttsx3_available:
                self._select_voice_for_language()
                if self.current_voice:
                    print(f"TTS language changed to {self.language.upper()}, using voice: {self.current_voice}")
                else:
                    print(f"TTS language changed to {self.language.upper()}, using default voice")
    
    def list_voices(self):
        """List all available voices (for debugging)"""
        print("\n=== Available TTS Voices ===")
        if hasattr(self, 'engine') and self.pyttsx3_available:
            try:
                voices = self.engine.getProperty('voices')
                if voices:
                    print(f"\npyttsx3 voices ({len(voices)} total):")
                    for i, voice in enumerate(voices, 1):
                        current = " [CURRENT]" if self.current_voice == voice.name else ""
                        print(f"  {i}. {voice.name}{current}")
                        print(f"     ID: {voice.id}")
            except Exception as e:
                print(f"Error listing pyttsx3 voices: {e}")
        
        if sys.platform == 'win32':
            try:
                ps_command = '''
Add-Type -AssemblyName System.Speech
$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer
$voices = $speak.GetInstalledVoices()
Write-Host "`nPowerShell/Windows voices ($($voices.Count) total):"
foreach ($voice in $voices) {
    Write-Host "  - $($voice.VoiceInfo.Name)"
    Write-Host "    Culture: $($voice.VoiceInfo.Culture)"
}
'''
                result = subprocess.run(
                    ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_command],
                    timeout=10,
                    text=True,
                    capture_output=True
                )
                if result.stdout:
                    print(result.stdout)
            except Exception as e:
                print(f"Error listing PowerShell voices: {e}")
        print("=" * 30)


if __name__ == "__main__":
    # Test the TTS module
    tts = TTSModule(language='hindi')
    print("TTS module initialized successfully!")
    tts.speak("Hello, this is a test of the offline text to speech module.")
