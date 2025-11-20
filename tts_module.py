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
        self.piper_exe_path = None
        self.piper_model_path = None
        
        # Method 1: Try Piper TTS (neural TTS - completely offline, best for Hindi and Telugu)
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
            # Only set as primary if Piper is not available
            if not self.piper_available:
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
        """Initialize Piper TTS (offline neural TTS - best for Hindi and Telugu)"""
        # Check for local piper.exe in piper folder
        piper_dir = os.path.join(os.getcwd(), 'piper')
        piper_exe = os.path.join(piper_dir, 'piper.exe')
        
        # Check if local piper.exe exists
        if os.path.exists(piper_exe):
            self.piper_exe_path = piper_exe
            print(f"Found local Piper TTS at: {piper_exe}")
        else:
            # Try system-wide piper
            try:
                result = subprocess.run(['piper', '--version'], capture_output=True, timeout=2, text=True)
                if result.returncode == 0:
                    self.piper_exe_path = 'piper'
                    print("Found system-wide Piper TTS")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                self.piper_available = False
                return
            except Exception as e:
                self.piper_available = False
                return
        
        # Find model for current language
        model_found = False
        
        if self.language == 'telugu':
            # Check for Telugu model
            telugu_model = os.path.join(piper_dir, 'te_IN-maya-medium.onnx')
            telugu_json = os.path.join(piper_dir, 'te_IN-maya-medium.onnx.json')
            
            if os.path.exists(telugu_model) and os.path.exists(telugu_json):
                self.piper_model_path = telugu_model
                self.piper_available = True
                model_found = True
                print(f"[SUCCESS] Found Telugu Piper model: te_IN-maya-medium")
            else:
                print(f"[WARNING] Telugu model not found at: {telugu_model}")
        
        elif self.language == 'hindi':
            # Check for Hindi model in piper folder - search for any hi_IN model
            hindi_models = [
                os.path.join(piper_dir, 'hi_IN-arya-medium.onnx'),
                os.path.join(piper_dir, 'hi_IN-arya-high.onnx'),
                os.path.join(piper_dir, 'hi_IN-arya-low.onnx'),
                os.path.join(piper_dir, 'hi_IN-kalpana-medium.onnx'),
                os.path.join(piper_dir, 'hi_IN-kalpana-high.onnx'),
                os.path.join(piper_dir, 'hi_IN-kalpana-low.onnx'),
                os.path.join(piper_dir, 'hi_IN-madhur-medium.onnx'),
                os.path.join(piper_dir, 'hi_IN-madhur-high.onnx'),
            ]
            
            # Also search for any file starting with hi_IN
            try:
                for file in os.listdir(piper_dir):
                    if file.startswith('hi_IN') and file.endswith('.onnx'):
                        model_path = os.path.join(piper_dir, file)
                        json_path = model_path + '.json'
                        if os.path.exists(json_path):
                            hindi_models.insert(0, model_path)  # Add to beginning of list
            except:
                pass
            
            for model_path in hindi_models:
                json_path = model_path + '.json'
                if os.path.exists(model_path) and os.path.exists(json_path):
                    self.piper_model_path = model_path
                    self.piper_available = True
                    model_found = True
                    model_name = os.path.basename(model_path).replace('.onnx', '')
                    print(f"[SUCCESS] Found Hindi Piper model: {model_name}")
                    break
            
            if not model_found:
                print(f"[WARNING] Hindi Piper model not found in piper folder")
                print(f"Expected files: hi_IN-*.onnx and hi_IN-*.onnx.json")
                print(f"\nTo download Hindi model:")
                print(f"1. Visit: https://huggingface.co/rhasspy/piper-voices/tree/main/hi_IN")
                print(f"2. Download: hi_IN-arya-medium.onnx and hi_IN-arya-medium.onnx.json")
                print(f"3. Save them to the 'piper' folder")
                print(f"\nOr use piper command:")
                print(f"  piper download --language hi_IN --output-dir piper")
        
        if model_found:
            self.tts_method = 'piper'
            print(f"[TTS] Using Piper TTS for {self.language.upper()}")
        else:
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
        
        # Try Piper first if available (best quality for Hindi and Telugu)
        if self.piper_available and self.piper_model_path:
            try:
                self._speak_piper(text)
                return
            except Exception as e:
                print(f"[TTS] Piper failed: {e}, using fallback...")
        
        # Use pyttsx3 or PowerShell for fallback
        if self.pyttsx3_available:
            self._speak_pyttsx3(text)
        elif self.powershell_available:
            self._speak_powershell(text)
        else:
            print(f"[WARNING] Could not speak text. No offline TTS method available.")
    
    def _speak_piper(self, text):
        """Speak using Piper TTS (offline neural TTS - best quality for Hindi and Telugu)"""
        try:
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                wav_path = tmp_file.name
            
            # Use local piper.exe with model
            cmd = [self.piper_exe_path, '--model', self.piper_model_path, '--output_file', wav_path]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=os.path.dirname(self.piper_exe_path) if self.piper_exe_path != 'piper' else None
            )
            stdout, stderr = process.communicate(input=text)
            
            if process.returncode == 0 and os.path.exists(wav_path):
                # Try multiple playback methods
                played = False
                
                # Method 1: Try pydub playback
                try:
                    from pydub import AudioSegment
                    from pydub.playback import play
                    audio = AudioSegment.from_wav(wav_path)
                    play(audio)
                    played = True
                except ImportError:
                    pass
                except Exception as e:
                    print(f"[DEBUG] pydub playback failed: {e}")
                
                # Method 2: Try winsound (Windows built-in)
                if not played and sys.platform == 'win32':
                    try:
                        import winsound
                        winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_NOWAIT)
                        played = True
                        import time
                        time.sleep(2)  # Wait for audio to play
                    except Exception as e:
                        print(f"[DEBUG] winsound failed: {e}")
                
                # Method 3: Try system command
                if not played:
                    if sys.platform == 'win32':
                        # Use PowerShell to play audio
                        ps_cmd = f'Add-Type -AssemblyName presentationCore; $mediaPlayer = New-Object system.windows.media.mediaplayer; $mediaPlayer.open([uri]"{os.path.abspath(wav_path).replace(chr(92), "/")}"); $mediaPlayer.Play(); Start-Sleep -Seconds 5'
                        try:
                            subprocess.run(['powershell', '-Command', ps_cmd], timeout=10, check=False)
                            played = True
                        except:
                            # Last resort: open with default player
                            os.system(f'start "" "{wav_path}"')
                            import time
                            time.sleep(2)
                    elif sys.platform == 'darwin':
                        os.system(f'afplay "{wav_path}"')
                    else:
                        os.system(f'aplay "{wav_path}" 2>/dev/null || paplay "{wav_path}" 2>/dev/null')
                
                # Clean up
                import time
                time.sleep(1)
                try:
                    os.remove(wav_path)
                except:
                    pass
                
                if played:
                    print(f"[TTS] Speech completed (Piper - {self.language.upper()})")
                else:
                    print(f"[TTS] Audio file generated but playback may have failed")
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
            
            # Ensure volume is set (max volume)
            self.engine.setProperty('volume', 1.0)
            self.engine.setProperty('rate', 150)
            
            # Try to save to file first, then play (more reliable)
            try:
                temp_wav = os.path.join(tempfile.gettempdir(), 'tts_output.wav')
                # Ensure text is properly encoded for pyttsx3
                try:
                    # Try to save with UTF-8 encoding
                    self.engine.save_to_file(text, temp_wav)
                except UnicodeEncodeError:
                    # Fallback: encode to ASCII with errors='ignore' for compatibility
                    text_ascii = text.encode('ascii', errors='ignore').decode('ascii')
                    self.engine.save_to_file(text_ascii, temp_wav)
                self.engine.runAndWait()
                
                # Wait for file to be created
                import time
                time.sleep(0.5)
                
                if os.path.exists(temp_wav):
                    # Play using winsound (Windows) or system command
                    if sys.platform == 'win32':
                        try:
                            import winsound
                            winsound.PlaySound(temp_wav, winsound.SND_FILENAME)
                        except:
                            # Fallback to PowerShell
                            ps_cmd = f'Add-Type -AssemblyName presentationCore; $mediaPlayer = New-Object system.windows.media.mediaplayer; $mediaPlayer.open([uri]"{os.path.abspath(temp_wav).replace(chr(92), "/")}"); $mediaPlayer.Play(); Start-Sleep -Seconds 5'
                            subprocess.run(['powershell', '-Command', ps_cmd], timeout=10, check=False)
                    else:
                        if sys.platform == 'darwin':
                            os.system(f'afplay "{temp_wav}"')
                        else:
                            os.system(f'aplay "{temp_wav}" 2>/dev/null || paplay "{temp_wav}" 2>/dev/null')
                    
                    # Clean up
                    time.sleep(0.5)
                    try:
                        os.remove(temp_wav)
                    except:
                        pass
            except Exception as e:
                print(f"[DEBUG] File-based playback failed: {e}, trying direct speak...")
                # Fallback to direct speak
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
            # If using Piper, save directly
            if self.piper_available and self.piper_model_path:
                try:
                    cmd = [self.piper_exe_path, '--model', self.piper_model_path, '--output_file', output_path]
                    process = subprocess.Popen(
                        cmd,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        cwd=os.path.dirname(self.piper_exe_path) if self.piper_exe_path != 'piper' else None
                    )
                    process.communicate(input=text)
                    if process.returncode == 0 and os.path.exists(output_path):
                        return output_path
                except Exception as e:
                    print(f"Piper synthesis error: {e}, falling back...")
            
            # Fallback to pyttsx3
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
            
            # Re-initialize Piper for Hindi and Telugu
            if self.language in ['hindi', 'telugu']:
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
        
        # Show Piper models if available
        if self.piper_available:
            print(f"\nPiper TTS: Available")
            print(f"  Model: {os.path.basename(self.piper_model_path)}")
            print(f"  Language: {self.language.upper()}")
        print("=" * 30)


if __name__ == "__main__":
    # Test the TTS module
    print("Testing Hindi TTS...")
    tts_hindi = TTSModule(language='hindi')
    tts_hindi.speak("नमस्ते, यह हिंदी टेक्स्ट टू स्पीच का परीक्षण है।")
    
    print("\nTesting Telugu TTS...")
    tts_telugu = TTSModule(language='telugu')
    tts_telugu.speak("నమస్కారం, ఇది తెలుగు టెక్స్ట్ టు స్పీచ్ పరీక్ష.")
