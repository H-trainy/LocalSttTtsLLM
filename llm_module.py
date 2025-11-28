# Try to import sarvamai
try:
    from sarvamai import SarvamAI
    SARVAM_AVAILABLE = True
except ImportError:
    SARVAM_AVAILABLE = False
    SarvamAI = None

# Try to import dotenv
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    load_dotenv = None

import os
import time

# Load .env file if available
if DOTENV_AVAILABLE:
    load_dotenv()

class LLMModule:
    def __init__(self, model_name='sarvam-m', api_key=None):
        """
        Initialize LLM module with Sarvam AI
        
        Args:
            model_name: Sarvam AI model name 
                - 'sarvam-m' (Sarvam's multilingual model, default - supports Hindi, English, etc.)
                - 'gemma-4b' (Google's Gemma 4B model)
                - 'gemma-12b' (Google's Gemma 12B model)
            api_key: Sarvam AI API key (if None, reads from SARVAM_API_KEY env var)
        """
        # Map old model names to new ones for backward compatibility
        model_mapping = {
            'openhathi-hi': 'sarvam-m',
            'openhathi-en': 'sarvam-m',
            'openhathi': 'sarvam-m'
        }
        self.model_name = model_mapping.get(model_name, model_name)
        self._init_sarvam(api_key)
    
    def _init_sarvam(self, api_key=None):
        """Initialize Sarvam AI connection"""
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv('SARVAM_API_KEY')
        
        # Clean up the API key if it contains command text
        if self.api_key:
            self.api_key = self.api_key.replace('set SARVAM_API_KEY=', '').replace('export SARVAM_API_KEY=', '')
            self.api_key = self.api_key.strip().strip('"').strip("'")
        
        if not self.api_key:
            raise ValueError("Sarvam AI API key required. Set SARVAM_API_KEY environment variable or pass api_key parameter.")
        
        # Validate API key format (Sarvam keys typically start with 'sk_')
        if not self.api_key.startswith('sk_'):
            print(f"\n⚠️  WARNING: Sarvam AI keys typically start with 'sk_'. Your key starts with: {self.api_key[:7]}...")
            print("Please verify your API key at https://dashboard.sarvam.ai/")
        
        print(f"Initialized Sarvam AI. Using model: {self.model_name}")
        print(f"API key: {self.api_key[:10]}... (length: {len(self.api_key)})")
        self.client = None  # We'll use direct HTTP requests instead of the SDK

    def generate(self, prompt, system_prompt=None, max_tokens=100, temperature=0.6, max_retries=3):
        """Generate response from Sarvam AI with retry logic"""
        return self._generate_sarvam(prompt, system_prompt, max_tokens, temperature, max_retries)
    
    def _generate_sarvam(self, prompt, system_prompt=None, max_tokens=100, temperature=0.6, max_retries=3):
        """Generate using Sarvam AI API with retry logic for rate limits"""
        import requests
        
        # Combine system prompt and user prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Use Sarvam AI's actual API endpoint
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Retry logic for rate limits
        for attempt in range(max_retries):
            try:
                # Sarvam AI chat completions endpoint
                response = requests.post(
                    "https://api.sarvam.ai/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                # Handle rate limit (429) with exponential backoff
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 2  # 2, 4, 8 seconds
                        print(f"⚠️  Rate limit hit. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                        time.sleep(wait_time)
                        continue
                    else:
                        error_detail = response.text
                        raise RuntimeError(f"Sarvam AI API error (status {response.status_code}): {error_detail}")
                
                # Check for other errors
                if response.status_code != 200:
                    error_detail = response.text
                    if response.status_code == 401 or response.status_code == 403:
                        raise ValueError(f"Invalid Sarvam AI API key. Status: {response.status_code}. Please check your API key at https://dashboard.sarvam.ai/")
                    else:
                        raise RuntimeError(f"Sarvam AI API error (status {response.status_code}): {error_detail}")
                
                result = response.json()
                
                # Extract the response text
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content'].strip()
                elif 'text' in result:
                    return result['text'].strip()
                else:
                    raise RuntimeError(f"Unexpected Sarvam AI response format: {result}")
                    
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 2
                    print(f"⚠️  Network error. Retrying in {wait_time}s... ({attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"\n[ERROR] Network error calling Sarvam AI: {e}")
                    return f"Error generating response: {e}"
            except Exception as e:
                error_str = str(e)
                if "api_key" in error_str.lower() or "authentication" in error_str.lower() or "401" in error_str or "403" in error_str:
                    print(f"\n[ERROR] Sarvam AI API authentication failed. Check your API key.")
                elif "rate limit" in error_str.lower() or "429" in error_str:
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 2
                        print(f"⚠️  Rate limit exceeded. Retrying in {wait_time}s... ({attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"\n[ERROR] Sarvam AI API rate limit exceeded after {max_retries} retries.")
                        print("Please wait a few minutes before trying again or reduce the number of requests.")
                else:
                    print(f"\n[ERROR] Sarvam AI API error: {e}")
                    print(f"Note: Check Sarvam AI documentation for correct API usage: https://docs.sarvam.ai/")
                return f"Error generating response: {e}"
        
        return "Error: Max retries exceeded"


if __name__ == "__main__":
    print("Testing with Sarvam AI...")
    llm = LLMModule()
    print("LLM initialized.")
    response = llm.generate("Hello, how are you?")
    print(f"Response: {response}")
