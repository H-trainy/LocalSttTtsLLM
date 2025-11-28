"""
Process first 5 rows from Transcript-24-11-2025.xlsx
Read transcriptions, generate summary and intent, save to IntentOfthetranscribetext.xlsx
"""

import os

# Load .env file FIRST, before anything else
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, '.env')

try:
    from dotenv import load_dotenv
    # Try loading from script directory
    if os.path.exists(env_path):
        # First, try to fix the .env file if it has 'set' keyword
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file has 'set' keyword and fix it
            if content.strip().startswith('set '):
                print("⚠️  Found 'set' keyword in .env file, fixing it...")
                # Remove 'set ' from the beginning of lines
                lines = content.split('\n')
                fixed_lines = []
                for line in lines:
                    if line.strip().startswith('set '):
                        # Remove 'set ' prefix
                        fixed_line = line.replace('set ', '', 1).strip()
                        fixed_lines.append(fixed_line)
                    else:
                        fixed_lines.append(line)
                
                # Write back the fixed content
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(fixed_lines))
                print("✓ Fixed .env file (removed 'set' keyword)")
            
            # Now load the .env file
            load_dotenv(env_path, override=True)
            print(f"✓ Loaded .env file from: {env_path}")
        except Exception as e:
            print(f"⚠️  Error reading/fixing .env file: {e}")
            # Try loading anyway
            load_dotenv(env_path, override=True)
    else:
        # Try current working directory
        load_dotenv(override=True)
        print("✓ Tried loading .env from current directory")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
except Exception as e:
    print(f"⚠️  Error loading .env: {e}")

from process_transcribe_to_excel import TranscribeProcessor

if __name__ == "__main__":
    print("="*60)
    print("Processing First 5 Rows from Excel")
    print("="*60)
    print()
    
    # Use Sarvam AI
    print("Using Sarvam AI for better accuracy with Indian languages")
    
    # Get API key from environment (should be loaded from .env)
    api_key = os.getenv('SARVAM_API_KEY')
    
    # Debug info
    print(f"\nDebug Info:")
    print(f"  .env file path: {env_path}")
    print(f"  .env file exists: {os.path.exists(env_path)}")
    if api_key:
        print(f"  API key found: Yes (length: {len(api_key)}, starts with: {api_key[:7]}...)")
    else:
        print(f"  API key found: No")
    
    # Clean up the API key if it contains command text
    if api_key:
        # Remove common prefixes if user copied the whole command
        api_key = api_key.replace('set SARVAM_API_KEY=', '').replace('export SARVAM_API_KEY=', '')
        api_key = api_key.strip().strip('"').strip("'")
    
    if not api_key or api_key.startswith('set ') or api_key.startswith('export '):
        print("\n⚠️  WARNING: SARVAM_API_KEY not found!")
        print(f"\nMake sure your .env file is at: {env_path}")
        print("\nThe .env file should contain exactly this line (no quotes, no spaces):")
        print("  SARVAM_API_KEY=your-sarvam-api-key-here")
        print("\nGet your API key from: https://dashboard.sarvam.ai/")
        print("\nOr enter the API key now:")
        api_key = input("\nEnter your Sarvam AI API Key: ").strip()
        api_key = api_key.strip('"').strip("'")
        
        if not api_key:
            print("\n❌ ERROR: API key required!")
            print("Get your API key from: https://dashboard.sarvam.ai/")
            exit(1)
    else:
        print(f"✓ Using API key from .env file")
    
    model = 'sarvam-m'  # Sarvam's multilingual model (supports Hindi, English, etc.)
    
    # Initialize processor
    print("\nInitializing processor...")
    processor = TranscribeProcessor(
        excel_file='IntentOfthetranscribetext.xlsx',
        llm_model=model,
        language='hindi',
        api_key=api_key
    )
    
    # Process from source Excel file (first 5 rows)
    source_file = 'Transcript-24-11-2025.xlsx'
    
    if not os.path.exists(source_file):
        print(f"\n❌ ERROR: Source file not found: {source_file}")
        print("Please make sure the file exists in the current directory.")
        exit(1)
    
    print(f"\n📖 Reading from: {source_file}")
    print(f"💾 Saving to: IntentOfthetranscribetext.xlsx")
    print(f"📊 Processing first 5 rows...\n")
    
    try:
        processor.process_from_excel(source_file, limit=5000)
        print("\n" + "="*60)
        print("✅ Processing Complete!")
        print("="*60)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
