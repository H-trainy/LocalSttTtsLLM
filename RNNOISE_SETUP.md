# RNNoise & WebRTC Noise Cancellation Setup

This guide explains how to set up RNNoise and WebRTC for offline noise cancellation.

## Quick Setup

### Step 1: Install WebRTC (Required)

```bash
pip install webrtcvad scipy
```

This provides:
- **Voice Activity Detection (VAD)** - Removes silence automatically
- **Spectral Noise Suppression** - Reduces background noise

### Step 2: Download RNNoise DLL (Optional, but Recommended)

For best quality noise reduction:

1. **Download RNNoise DLL:**
   - **Option A: DLLme.com (Easy)**
     - Visit: https://dllme.com/dll/files/rnnoise
     - Download the 64-bit version (x86-64)
     - Save as `rnnoise_mono.dll` or `rnnoise.dll`
   
   - **Option B: Alternative Sources**
     - Search for "rnnoise.dll download" or "rnnoise_mono.dll"
     - Make sure to download 64-bit (x64) version for Windows

2. **Place the DLL:**
   - **Recommended:** Place in piper folder: `piper/rnnoise_mono.dll`
   - **Alternative:** Place in project root: `rnnoise.dll` or `rnnoise_mono.dll`

3. **The code will automatically detect and use it!**

**Note:** The code supports both `rnnoise.dll` and `rnnoise_mono.dll` filenames.

## How It Works

### Priority Order:
1. **RNNoise** (if DLL found) - Best quality, real-time
2. **WebRTC VAD + Spectral Subtraction** (fallback) - Good quality, always available

### Features:

**RNNoise:**
- ✅ Real-time noise cancellation
- ✅ Removes: fan noise, background hum, static, mic hiss
- ✅ Works on CPU, even low-power systems
- ✅ Extremely fast

**WebRTC:**
- ✅ Voice Activity Detection (removes silence)
- ✅ Spectral noise suppression
- ✅ Automatic Gain Control (AGC)
- ✅ Works 100% offline

## Testing

Test if noise reduction is working:

```python
from noise_reduction import NoiseReducer

reducer = NoiseReducer()
print(f"RNNoise available: {reducer.rnnoise_available}")
print(f"WebRTC available: {reducer.webrtc_available}")

# Test on an audio file
reducer.reduce_noise("test_audio.wav", "test_audio_clean.wav")
```

## Benefits

- **Clearer Audio Input** - Better transcription accuracy
- **Reduced Background Noise** - Fan, hum, static removed
- **Automatic Silence Removal** - Only processes speech
- **100% Offline** - No internet needed
- **Fast Processing** - Real-time capable

## Troubleshooting

### "RNNoise DLL not found"
- Download from: https://dllme.com/dll/files/rnnoise (or search for "rnnoise.dll download")
- Place `rnnoise.dll` or `rnnoise_mono.dll` in:
  - `piper/rnnoise_mono.dll` (recommended)
  - OR project root: `rnnoise.dll`

### "webrtcvad not installed"
```bash
pip install webrtcvad
```

### "No noise reduction available"
- Install: `pip install webrtcvad scipy`
- The system will use WebRTC (always works)

## Notes

- RNNoise provides the best quality but requires the DLL
- WebRTC works immediately after `pip install webrtcvad`
- Both methods work 100% offline
- Noise reduction is applied automatically to all recordings

