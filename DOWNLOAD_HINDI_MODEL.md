# Download Hindi TTS Model for Piper

You have the safetensors file (`model-00003-of-00003.safetensors`) but need the ONNX model files for Piper TTS to work with Hindi.

## Quick Download

### Option 1: Direct Download (Recommended)

1. **Download Hindi Model Files:**
   - Visit: https://huggingface.co/rhasspy/piper-voices/tree/main/hi_IN/arya/medium
   - Download these two files:
     - `model.onnx` (rename to `hi_IN-arya-medium.onnx`)
     - `model.onnx.json` (rename to `hi_IN-arya-medium.onnx.json`)
   - Save both files to your `piper` folder

### Option 2: Using Piper Command

If you have piper installed system-wide:

```bash
piper download --language hi_IN --voice arya --quality medium --output-dir piper
```

### Option 3: Using wget/curl

**For Windows PowerShell:**
```powershell
# Download model file
Invoke-WebRequest -Uri "https://huggingface.co/rhasspy/piper-voices/resolve/main/hi_IN/arya/medium/model.onnx" -OutFile "piper\hi_IN-arya-medium.onnx"

# Download config file
Invoke-WebRequest -Uri "https://huggingface.co/rhasspy/piper-voices/resolve/main/hi_IN/arya/medium/model.onnx.json" -OutFile "piper\hi_IN-arya-medium.onnx.json"
```

## After Download

Once you have both files in the `piper` folder:
- `hi_IN-arya-medium.onnx`
- `hi_IN-arya-medium.onnx.json`

The TTS module will automatically detect and use them for Hindi text-to-speech!

## Alternative Models

You can also use:
- `hi_IN-kalpana-medium` - Different voice
- `hi_IN-madhur-medium` - Another voice option

Just download the corresponding `.onnx` and `.onnx.json` files.

