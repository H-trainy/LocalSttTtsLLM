# Local AI Voice Agent - 100% OFFLINE

A simple offline AI agent that listens to your voice, understands it, and responds with speech. Works completely offline after initial setup.

## What It Does

1. 🎤 **Listens** - Records your voice from microphone or audio file (with noise reduction)
2. 🔍 **Understands** - Converts speech to text (supports Hindi, English, Urdu, Telugu)
3. 🧠 **Thinks** - Uses local AI (Ollama) to generate intelligent responses
4. 🔊 **Speaks** - Converts response back to speech in your language (Piper TTS for Hindi/Telugu)
5. 💾 **Saves** - Automatically saves transcription and response to text files

**100% OFFLINE** - No internet needed after first setup!

## Quick Start

### 1. Install Requirements

```bash
pip install -r requirements.txt
```

**Windows users**: If PyAudio fails, try:
```bash
pip install pipwin
pipwin install pyaudio
```

### 2. Install Ollama

Download from: https://ollama.ai/

Then pull a model (default is phi3 - fast and lightweight):
```bash
ollama pull phi3
```

Other model options:
```bash
ollama pull phi3:mini      # Smaller, faster
ollama pull llama3.1:8b    # Larger, more capable
ollama pull llama3.1:70b   # Very large (requires more RAM/VRAM)
```

### 3. Start Ollama

```bash
ollama serve
```

Keep this running in a separate terminal.

### 4. Run the Agent

```bash
python ai_agent.py
```

## How to Use

### Basic Usage

1. **Start the agent**: `python ai_agent.py`
2. **Select language**: Type `hindi`, `english`, `urdu`, or `telugu`
3. **Record**: Press ENTER to record from microphone
   - Speak your question
   - Recording stops after 5 seconds of silence
4. **Listen**: The AI will respond with voice

### Input Options

- **Microphone**: Press ENTER or type `mic`
- **Audio File**: Type the file path (e.g., `audio.wav`)

### Language Commands

- `hindi` or `lang:hindi` - Switch to Hindi
- `english` or `lang:english` - Switch to English
- `urdu` or `lang:urdu` - Switch to Urdu
- `telugu` or `lang:telugu` - Switch to Telugu
- `auto` - Enable automatic language detection
- `manual` - Disable auto-detection
- `voices` - List all available TTS voices

### Example Session

```
Enter command: telugu
Language set to: TELUGU

Enter command: [Press ENTER]
Recording voice input...
[Speak in Telugu]
Transcribed: నమస్కారం
LLM Response: నమస్కారం! మీరు ఎలా ఉన్నారు?
[TTS] Speaking in TELUGU...
```

## Project Files

- `ai_agent.py` - Main program (run this)
- `stt_module.py` - Speech-to-Text (faster-whisper)
- `tts_module.py` - Text-to-Speech (Piper TTS + system voices)
- `llm_module.py` - AI brain (Ollama)
- `voice_recorder.py` - Audio recording with noise reduction
- `noise_reduction.py` - WebRTC noise cancellation
- `language_detector.py` - Auto language detection

## Models Used

### Speech-to-Text
- **faster-whisper** (large-v3) - High accuracy, fast, 100% offline

### Text-to-Speech
- **Piper TTS** - Neural TTS for Hindi and Telugu (best quality)
- **pyttsx3** - System voices (fallback for all languages)
- **PowerShell TTS** - Windows backup (offline)

### AI Model
- **Ollama** - Local AI, no internet needed
  - Default: `phi3` (fast, lightweight)
  - Options: `phi3:mini`, `llama3.1:8b`, `llama3.1:70b`

### Noise Reduction
- **WebRTC VAD** - Voice Activity Detection and noise suppression
- Automatically applied to all recordings for clearer audio

**All models are public - No tokens or API keys required!**

## First Run

On first run, the system will download models:
- **faster-whisper large-v3** (~1.5GB) - High accuracy speech recognition
- **Language detector models** (~300MB) - Only if auto-detection is enabled

**Requires internet only for first download. After that, works 100% offline!**

## Features

### Automatic Text Saving
All transcriptions and AI responses are automatically saved to text files:
- Saved in `output_text/` folder
- Named after the audio file (e.g., `audio.wav` → `audio.txt`)
- Includes transcription, AI response, language, and timestamp

### Noise Reduction
- Automatic noise cancellation using WebRTC
- Removes background noise and silence
- Improves transcription accuracy

## Troubleshooting

### No Audio Output
- Check system volume
- Install language pack in Windows (Settings > Language)
- Type `voices` to see available voices
- For Hindi/Telugu: Ensure Piper TTS models are in `piper/` folder
  - Hindi: `hi_IN-*.onnx` and `hi_IN-*.onnx.json`
  - Telugu: `te_IN-maya-medium.onnx` and `te_IN-maya-medium.onnx.json`
- See `DOWNLOAD_HINDI_MODEL.md` for Hindi TTS setup

### Ollama Not Working
- Make sure Ollama is running: `ollama serve`
- Check model is installed: `ollama list`
- Pull default model: `ollama pull phi3`
- For other models: `ollama pull phi3:mini` or `ollama pull llama3.1:8b`
- If you get "model not found" error, verify the model name with: `ollama list`

### Recording Issues
- Check microphone permissions
- Verify PyAudio is installed
- Try different microphone

### Language Not Working
- Install language pack in Windows
- Type `voices` to check available voices
- Use manual language selection: `lang:hindi`

## Requirements

- Python 3.8+
- Ollama installed and running
- Microphone and speakers
- Windows/Linux/MacOS

## Notes

- **Privacy**: Everything runs on your computer, nothing sent online
- **Offline**: Works without internet after first setup
- **Free**: All models are free and public
- **Fast**: Processing happens locally on your machine

---

**Made for offline AI voice assistants** 🎤🤖
