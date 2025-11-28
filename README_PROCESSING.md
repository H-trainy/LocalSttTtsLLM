# Transcription Processing with Sarvam AI

This project processes transcribed text from Excel files, generates summaries and extracts intents using Sarvam AI.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Sarvam AI API Key

Create a `.env` file in this directory:
```
SARVAM_API_KEY=your-api-key-here
```

Get your API key from: https://dashboard.sarvam.ai/

### 3. Run the Script

Process first 5 rows from Excel:
```bash
python process_5_rows.py
```

Process from command line:
```bash
python process_transcribe_to_excel.py --source-excel Transcript-24-11-2025.xlsx --limit 5
```

## What It Does

1. Reads transcriptions from `Transcript-24-11-2025.xlsx`
2. For each transcription:
   - Generates **Summary** (English, one sentence)
   - Extracts **Intent** (2-3 words, e.g., "power cut", "complaint")
3. Saves results to `IntentOfthetranscribetext.xlsx`

## Output Format

Excel file columns:
- **Audio Name**: From source file
- **Transcribe**: Original transcribed text
- **Summary**: One sentence summary in English
- **Intent**: 2-3 word intent (e.g., "power cut")

## Files

- `process_5_rows.py` - Simple script to process first 5 rows
- `process_transcribe_to_excel.py` - Main processing script
- `llm_module.py` - Sarvam AI integration
- `intent_analyzer.py` - Intent extraction module

## See Also

- `SARVAM_SETUP.md` - Detailed Sarvam AI setup guide

