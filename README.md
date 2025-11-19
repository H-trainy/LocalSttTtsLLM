# Local AI Voice Agent - 100% OFFLINE

A simple offline AI agent that listens to your voice, understands it, and responds with speech. Works completely offline after initial setup.

## What It Does

1. 🎤 **Listens** - Records your voice from microphone or audio file
2. 🔍 **Understands** - Converts speech to text (supports Hindi, English, Urdu, Telugu)
3. 🧠 **Thinks** - Uses local AI (Ollama) to generate intelligent responses
4. 🔊 **Speaks** - Converts response back to speech in your language

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

Then pull a model:
```bash
ollama pull phi3:mini
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
- `stt_module.py` - Speech-to-Text (Whisper)
- `tts_module.py` - Text-to-Speech (system voices)
- `llm_module.py` - AI brain (Ollama)
- `voice_recorder.py` - Audio recording
- `language_detector.py` - Auto language detection

## Models Used

### Speech-to-Text
- **Whisper** (primary) - High accuracy, offline
- **Wav2Vec2** (fallback) - Backup option

### Text-to-Speech
- **pyttsx3** - Uses system voices (offline)
- **PowerShell TTS** - Windows backup (offline)

### AI Model
- **Ollama Phi3** - Local AI, no internet needed

**All models are public - No tokens or API keys required!**

## First Run

On first run, the system will download models (~500MB-1GB):
- Whisper model (~150MB)
- Wav2Vec2 models (~300MB each)

**Requires internet only for first download. After that, works 100% offline!**

## Troubleshooting

### No Audio Output
- Check system volume
- Install language pack in Windows (Settings > Language)
- Type `voices` to see available voices
- See `TELUGU_TTS_SETUP.md` for Telugu setup help

### Ollama Not Working
- Make sure Ollama is running: `ollama serve`
- Check model is installed: `ollama list`
- Pull model if missing: `ollama pull phi3:mini`

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
