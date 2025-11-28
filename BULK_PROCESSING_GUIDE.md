# Bulk Processing Guide

## Quick Start

### 1. Process 50 rows (Recommended - Balanced speed & reliability)
```bash
python process_bulk_optimized.py Transcript-24-11-2025.xlsx 50 5
```

### 2. Process 100 rows
```bash
python process_bulk_optimized.py Transcript-24-11-2025.xlsx 100 5
```

### 3. Process ALL rows (2740 rows - will take ~2-3 hours)
```bash
python process_bulk_optimized.py Transcript-24-11-2025.xlsx 2740 5
```

## Processing Scripts Comparison

### 1. `process_5_rows.py` - Testing/Demo
- **Speed**: Slowest (sequential)
- **Use**: Testing, debugging
- **Rows**: 5 rows only
- **Time**: ~30 seconds

### 2. `process_bulk_fast.py` - Fast but risky
- **Speed**: Fastest (3 concurrent workers)
- **Use**: When you have high rate limits
- **Risk**: May hit rate limits frequently
- **Time**: ~0.3 rows/second

### 3. `process_bulk_optimized.py` - Recommended ⭐
- **Speed**: Balanced (5 concurrent with delays)
- **Use**: Production bulk processing
- **Risk**: Low - smart rate limiting
- **Time**: ~0.5-1 rows/second
- **Reliability**: High

## Parameters

```bash
python process_bulk_optimized.py [source_file] [limit] [batch_size]
```

- **source_file**: Excel file with transcriptions (default: Transcript-24-11-2025.xlsx)
- **limit**: Number of rows to process (default: 50)
- **batch_size**: Concurrent requests per batch (default: 5, max recommended: 10)

## Tips for Faster Processing

### 1. Increase batch size (if no rate limits)
```bash
python process_bulk_optimized.py Transcript-24-11-2025.xlsx 100 10
```

### 2. Reduce delay in code
Edit `process_bulk_optimized.py`:
```python
self.rate_limit_delay = 0.5  # Change from 1.5 to 0.5
```

### 3. Use multiple API keys (if available)
- Split your Excel file into chunks
- Run multiple instances with different API keys
- Merge results later

### 4. Process overnight
For all 2740 rows:
```bash
python process_bulk_optimized.py Transcript-24-11-2025.xlsx 2740 5
```
Estimated time: 2-3 hours

## Rate Limits

Sarvam AI free tier typically allows:
- ~60 requests per minute
- ~1000 requests per hour

Our optimized script respects these limits with:
- 1.5s delay between requests
- Batch processing with pauses
- Automatic retry on rate limit errors

## Monitoring Progress

The script shows real-time progress:
```
📦 Batch 1/10 (5 rows)
  ✓ Row 2 - 1/50
  ✓ Row 3 - 2/50
  ✓ Row 4 - 3/50
```

## Output

Results are saved to: `IntentOfthetranscribetext.xlsx`

Columns:
1. Audio Name
2. Transcribe (original text)
3. Summary (English, 1 sentence)
4. Intent (2-3 words)

## Troubleshooting

### Rate Limit Errors
- Reduce batch_size: `python process_bulk_optimized.py file.xlsx 50 3`
- Increase delay in code (edit `rate_limit_delay`)
- Wait 5-10 minutes and retry

### Slow Processing
- Increase batch_size: `python process_bulk_optimized.py file.xlsx 50 10`
- Reduce delay in code
- Use `process_bulk_fast.py` if you have high rate limits

### Errors in Results
- Check your API key in `.env` file
- Verify source Excel file format
- Check internet connection

## Example: Process 500 rows efficiently

```bash
# Process in chunks of 100 with 5 concurrent requests
python process_bulk_optimized.py Transcript-24-11-2025.xlsx 100 5
# Wait 2 minutes
python process_bulk_optimized.py Transcript-24-11-2025.xlsx 200 5
# Wait 2 minutes
python process_bulk_optimized.py Transcript-24-11-2025.xlsx 300 5
# Continue...
```

Or just run once:
```bash
python process_bulk_optimized.py Transcript-24-11-2025.xlsx 500 5
```
