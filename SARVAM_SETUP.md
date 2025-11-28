# Sarvam AI Setup Guide

## Quick Setup

### 1. Install Sarvam AI SDK
```bash
pip install sarvamai
```

### 2. Get API Key
1. Go to https://dashboard.sarvam.ai/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key

### 3. Set API Key in .env File

Create a `.env` file in `Harsh/LocalSttTtsLLM/` directory:

```
SARVAM_API_KEY=your-api-key-here
```

**Important:** 
- No quotes around the key
- No spaces around the `=`
- No `set` keyword

### 4. Run the Script

```bash
cd Harsh\LocalSttTtsLLM
python process_5_rows.py
```

## Available Models

- `openhathi-hi` - Hindi (default)
- `openhathi-en` - English
- Other Sarvam models as available

## Benefits of Sarvam AI

✅ **Optimized for Indian Languages** - Better understanding of Hindi, Telugu, etc.
✅ **Cost-Effective** - Competitive pricing
✅ **Fast Response** - Low latency
✅ **No Local Setup** - Cloud-based, no downloads needed

## Troubleshooting

### "sarvamai not available"
- Install with: `pip install sarvamai`

### "Invalid API key"
- Check your API key at https://dashboard.sarvam.ai/
- Make sure `.env` file has correct format: `SARVAM_API_KEY=your-key`

### API Errors
- Check your API key is valid
- Ensure you have credits/quota in your Sarvam AI account
- Visit https://docs.sarvam.ai/ for API documentation

