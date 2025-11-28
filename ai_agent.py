"""
Main AI Agent that orchestrates STT, LLM, and TTS
Simple voice recognition → LLM → Text-to-Speech pipeline
"""
import os
from datetime import datetime
from stt_module import STTModule
from tts_module import TTSModule
from llm_module import LLMModule
from voice_recorder import VoiceRecorder
from intent_analyzer import IntentAnalyzer


class AIAgent:
    def __init__(self, language='hindi', llm_model='phi3', auto_detect_language=True):
        """
        Initialize AI Agent
        
        Args:
            language: 'hindi', 'english', 'urdu', or 'telugu' (default language, used as fallback)
            llm_model: Ollama model name (default: 'phi3' - fast, no large downloads)
                       Other options: 'phi3:mini', 'llama3.1:8b', 'tinyllama'
            auto_detect_language: If True, automatically detect language from voice input (default: True)
        """
        self.language = language.lower()
        self.auto_detect_language = auto_detect_language
        
        if self.auto_detect_language:
            print("Initializing AI Agent with automatic language detection")
        else:
            print(f"Initializing AI Agent with language: {self.language.upper()}")
        
        # Initialize modules
        print("Loading STT module with Whisper...")
        self.stt = STTModule(use_whisper=True)
        
        print("Loading TTS module...")
        self.tts = TTSModule(language=self.language)
        
        print("Loading LLM module...")
        self.llm = LLMModule(model_name=llm_model)
        
        print("Loading Intent Analyzer module...")
        self.intent_analyzer = IntentAnalyzer(llm_model=llm_model)
        
        print("Initializing voice recorder...")
        self.recorder = VoiceRecorder()
        
        # Create temp directory for audio files
        self.temp_dir = "temp_audio"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Create output directory for text files
        self.output_dir = "output_text"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # System prompts for intelligent responses
        self.system_prompts = {
            'hindi': 'आप एक बुद्धिमान और सहायक AI सहायक हैं। उपयोगकर्ता के प्रश्नों का स्पष्ट, संक्षिप्त और उपयोगी उत्तर दें। हमेशा सही और प्रासंगिक जानकारी प्रदान करें।',
            'english': 'You are an intelligent and helpful AI assistant. Provide clear, concise, and useful responses to user questions. Always give accurate and relevant information.',
            'urdu': 'آپ ایک ذہین اور مددگار AI معاون ہیں۔ صارف کے سوالات کا واضح، مختصر اور مفید جواب دیں۔ ہمیشہ درست اور متعلقہ معلومات فراہم کریں۔',
            'telugu': 'మీరు ఒక తెలివైన మరియు సహాయక AI సహాయకుడు. వినియోగదారు ప్రశ్నలకు స్పష్టమైన, సంక్షిప్తమైన మరియు ఉపయోగకరమైన సమాధానాలు ఇవ్వండి. ఎల్లప్పుడూ ఖచ్చితమైన మరియు సంబంధిత సమాచారాన్ని అందించండి.'
        }
        
        print("AI Agent initialized successfully!")
    
    def process_voice_input(self, audio_path=None):
        """
        Process voice input: Record → STT → LLM → TTS → Play
        
        Args:
            audio_path: Path to existing audio file (optional)
        
        Returns:
            Dictionary with transcription, response, and audio path
        """
        try:
            # Step 1: Record or use provided audio
            if audio_path is None:
                input_audio_path = os.path.join(self.temp_dir, "input.wav")
                print("\nRecording voice input... (speak now, stops after 5 seconds of silence)")
                self.recorder.record_until_silence(output_path=input_audio_path)
            else:
                input_audio_path = audio_path
                print(f"Using provided audio file: {audio_path}")
            
            # Step 2: Speech-to-Text (with automatic language detection if enabled)
            # Note: Noise reduction is already applied during recording
            print("Converting speech to text...")
            
            # Transcribe (language detection happens inside STT module if enabled)
            transcription = self.stt.transcribe(input_audio_path)
            print(f"Transcribed: {transcription}")
            
            if not transcription or transcription.strip() == "":
                return {
                    'error': 'No speech detected in audio',
                    'transcription': '',
                    'analysis': {'summary': '', 'keywords': [], 'intent': ''},
                    'response': ''
                }
            
            # Update language if auto-detection changed it (STT module updates its own language)
            if self.auto_detect_language and hasattr(self.stt, 'language') and self.stt.language != self.language:
                self.language = self.stt.language
                self.tts.set_language(self.language)
                print(f"Language automatically detected and set to: {self.language.upper()}")
            
            # Step 2.5: Analyze transcription (Summary, Keywords, Intent)
            print("Analyzing transcription (Summary, Keywords, Intent)...")
            analysis = self.intent_analyzer.analyze(transcription, language=self.language)
            print(f"Summary: {analysis.get('summary', 'N/A')}")
            print(f"Keywords: {', '.join(analysis.get('keywords', []))}")
            print(f"Intent: {analysis.get('intent', 'N/A')}")
            
            # Step 3: LLM Processing
            print("Processing with LLM...")
            system_prompt = self.system_prompts.get(self.language, self.system_prompts['english'])
            response = self.llm.generate(
                prompt=transcription,
                system_prompt=system_prompt,
                max_tokens=256,  # Increased from 128 for clearer, complete responses
                temperature=0.4  # Lower temperature for more focused, coherent responses
            )
            print(f"LLM Response: {response}")
            
            # Step 4: Text-to-Speech and Play
            print("Converting to speech and playing...")
            
            # Speak the input transcription first
            print("Speaking input transcription...")
            if self.language == 'hindi':
                input_prefix = "आपने कहा: "
            elif self.language == 'telugu':
                input_prefix = "మీరు చెప్పారు: "
            elif self.language == 'urdu':
                input_prefix = "آپ نے کہا: "
            else:  # english
                input_prefix = "You said: "
            
            self.tts.speak(input_prefix + transcription)
            
            # Add a small pause
            import time
            time.sleep(0.5)
            
            # Then speak the AI response
            print("Speaking AI response...")
            if self.language == 'hindi':
                response_prefix = "AI ने उत्तर दिया: "
            elif self.language == 'telugu':
                response_prefix = "AI సమాధానం: "
            elif self.language == 'urdu':
                response_prefix = "AI کا جواب: "
            else:  # english
                response_prefix = "AI replied: "
            
            self.tts.speak(response_prefix + response)
            
            # Step 5: Save transcription, analysis, and response to text file
            text_file_path = self._save_to_text_file(input_audio_path, transcription, response, analysis)
            
            return {
                'transcription': transcription,
                'analysis': analysis,
                'response': response,
                'input_audio_path': input_audio_path,
                'text_file_path': text_file_path
            }
        
        except Exception as e:
            error_msg = f"Error in process_voice_input: {e}"
            print(f"\n[ERROR] {error_msg}")
            return {
                'error': error_msg,
                'transcription': '',
                'analysis': {'summary': '', 'keywords': [], 'intent': ''},
                'response': ''
            }
    
    def _save_to_text_file(self, audio_path, transcription, response, analysis=None):
        """
        Save transcription, analysis, and response to a text file named after the audio file
        
        Args:
            audio_path: Path to the audio file
            transcription: Transcribed text
            response: AI response text
            analysis: Analysis dictionary with summary, keywords, and intent (optional)
        
        Returns:
            Path to the saved text file
        """
        try:
            # Get base name of audio file (without extension)
            audio_basename = os.path.splitext(os.path.basename(audio_path))[0]
            
            # If it's a recorded file (input.wav), use timestamp
            if audio_basename == "input":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                text_filename = f"recording_{timestamp}.txt"
            else:
                text_filename = f"{audio_basename}.txt"
            
            # Create full path for text file
            text_file_path = os.path.join(self.output_dir, text_filename)
            
            # Prepare content
            content = f"Audio File: {os.path.basename(audio_path)}\n"
            content += f"Language: {self.language.upper()}\n"
            content += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            content += f"{'='*60}\n\n"
            content += f"TRANSCRIPTION:\n{'-'*60}\n{transcription}\n\n"
            
            # Add analysis section if available
            if analysis:
                content += f"ANALYSIS:\n{'-'*60}\n"
                if analysis.get('summary'):
                    content += f"SUMMARY: {analysis['summary']}\n"
                if analysis.get('keywords'):
                    keywords_str = ', '.join(analysis['keywords'])
                    content += f"KEYWORDS: {keywords_str}\n"
                if analysis.get('intent'):
                    content += f"INTENT: {analysis['intent']}\n"
                content += "\n"
            
            content += f"AI RESPONSE:\n{'-'*60}\n{response}\n"
            
            # Write to file
            with open(text_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\n[SUCCESS] Text saved to: {text_file_path}")
            return text_file_path
            
        except Exception as e:
            print(f"[WARNING] Failed to save text file: {e}")
            return None
    
    def set_language(self, language):
        """
        Change language for STT and TTS
        
        Args:
            language: 'hindi', 'english', or 'urdu'
        """
        if language.lower() != self.language:
            self.language = language.lower()
            print(f"Switching language to: {self.language}")
            self.stt.set_language(self.language)
            self.tts.set_language(self.language)
    
    def interactive_mode(self):
        """Run agent in interactive mode"""
        print("\n" + "="*60)
        print("AI Agent - Interactive Mode")
        print("="*60)
        if self.auto_detect_language:
            print("Mode: Automatic Language Detection (Hindi/English/Urdu/Telugu)")
        else:
            print(f"Current Language: {self.language.upper()}")
        print("\nCommands:")
        print("  - Press ENTER or type 'mic' to record from microphone")
        print("  - Type file path to process an audio file (e.g., 'audio.wav')")
        print("  - Language Selection:")
        print("    * 'hindi' or 'lang:hindi' - Switch to Hindi")
        print("    * 'english' or 'lang:english' - Switch to English")
        print("    * 'urdu' or 'lang:urdu' - Switch to Urdu")
        print("    * 'telugu' or 'lang:telugu' - Switch to Telugu")
        print("    * 'auto' or 'autodetect' - Enable automatic language detection")
        print("    * 'manual' - Disable auto-detection, use selected language")
        print("  - Type 'voices' to list all available TTS voices")
        print("  - Type 'quit' or 'exit' to stop")
        print("="*60 + "\n")
        
        while True:
            try:
                user_input = input("\nEnter command (ENTER/mic for microphone, file path for audio file): ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                # Handle language change
                user_input_lower = user_input.lower().strip()
                
                # Direct language commands (e.g., "hindi", "english")
                if user_input_lower in ['hindi', 'english', 'urdu', 'telugu']:
                    self.auto_detect_language = False
                    self.set_language(user_input_lower)
                    print(f"Language set to: {user_input_lower.upper()}")
                    print("Auto-detection disabled. Using selected language.")
                    continue
                
                # Language commands with prefix (e.g., "lang:hindi")
                if user_input_lower.startswith('lang:'):
                    new_lang = user_input_lower.split(':')[1].strip()
                    if new_lang in ['hindi', 'english', 'urdu', 'telugu']:
                        self.auto_detect_language = False
                        self.set_language(new_lang)
                        print(f"Language set to: {new_lang.upper()}")
                        print("Auto-detection disabled. Using selected language.")
                    else:
                        print("Invalid language. Use: hindi, english, urdu, or telugu")
                    continue
                
                # Toggle auto-detection
                if user_input_lower in ['auto', 'autodetect', 'auto-detect']:
                    self.auto_detect_language = True
                    self.stt.auto_detect = True
                    print("Automatic language detection ENABLED")
                    continue
                
                if user_input_lower in ['manual', 'disable-auto']:
                    self.auto_detect_language = False
                    self.stt.auto_detect = False
                    print(f"Automatic language detection DISABLED")
                    print(f"Using language: {self.language.upper()}")
                    continue
                
                # List available voices
                if user_input_lower in ['voices', 'list-voices', 'voice']:
                    self.tts.list_voices()
                    continue
                
                # Handle audio file input
                # Check if input is a file path (starts with 'file:' or is a valid file path)
                audio_file_path = None
                
                if user_input.lower().startswith('file:'):
                    # Extract path after 'file:' prefix
                    audio_file_path = user_input[5:].strip()
                elif user_input.lower() not in ['', 'mic', 'microphone']:
                    # Check if input looks like a file path (has extension or is a path)
                    audio_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.wma']
                    if any(user_input.lower().endswith(ext) for ext in audio_extensions) or os.sep in user_input or ':' in user_input:
                        audio_file_path = user_input
                
                if audio_file_path:
                    # Try to find the file
                    found_path = None
                    
                    # Check if it's an absolute path
                    if os.path.isabs(audio_file_path):
                        if os.path.exists(audio_file_path):
                            found_path = audio_file_path
                    else:
                        # Check relative to current directory
                        if os.path.exists(audio_file_path):
                            found_path = os.path.abspath(audio_file_path)
                        # Check relative to project directory
                        elif os.path.exists(os.path.join(os.getcwd(), audio_file_path)):
                            found_path = os.path.abspath(os.path.join(os.getcwd(), audio_file_path))
                        # Check in temp_audio directory
                        elif os.path.exists(os.path.join(self.temp_dir, audio_file_path)):
                            found_path = os.path.abspath(os.path.join(self.temp_dir, audio_file_path))
                    
                    if found_path:
                        print(f"Processing audio file: {found_path}")
                        result = self.process_voice_input(audio_path=found_path)
                    else:
                        print(f"Error: File not found: {audio_file_path}")
                        print(f"  Searched in: {os.getcwd()}")
                        print(f"  Please check the file path and try again.")
                        continue
                
                # Handle microphone input (default)
                elif user_input.lower() in ['', 'mic', 'microphone']:
                    result = self.process_voice_input()
                
                else:
                    print("Invalid command. Use ENTER/mic for microphone or provide a file path for audio file.")
                    continue
                
                if 'error' in result:
                    print(f"\n[ERROR] {result['error']}")
                else:
                    print(f"\n[SUCCESS]")
                    print(f"You said: {result['transcription']}")
                    if 'analysis' in result and result['analysis']:
                        analysis = result['analysis']
                        print(f"\nAnalysis:")
                        if analysis.get('summary'):
                            print(f"  Summary: {analysis['summary']}")
                        if analysis.get('keywords'):
                            print(f"  Keywords: {', '.join(analysis['keywords'])}")
                        if analysis.get('intent'):
                            print(f"  Intent: {analysis['intent']}")
                    print(f"AI replied: {result['response']}")
                    if 'text_file_path' in result and result['text_file_path']:
                        print(f"Text saved to: {result['text_file_path']}")
            
            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"\n[ERROR] {e}")
        
        # Cleanup
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up resources...")
        self.recorder.cleanup()
        print("Cleanup complete!")


if __name__ == "__main__":
    # Use Ollama by default (fast, no large downloads!)
    print("Using Ollama LLM (fast setup, no large downloads)")
    print("Model: phi3")
    print("Make sure Ollama is running: ollama serve")
    print("If model not found, run: ollama pull phi3")
    print()
    
    # Start with automatic language detection (enabled by default)
    agent = AIAgent(language='hindi', auto_detect_language=True)
    
    # Run in interactive mode
    agent.interactive_mode()
