# Try to import ollama
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ollama = None

class LLMModule:
    def __init__(self, model_name='phi3', host='http://localhost:11434'):
        """
        Initialize LLM module
        
        Args:
            model_name: Ollama model name (default: 'phi3')
            host: Ollama server host (default: 'http://localhost:11434')
        """
        self.model_name = model_name
        self.host = host
        self._init_ollama()
    
    def _init_ollama(self):
        """Initialize Ollama connection"""
        if not OLLAMA_AVAILABLE:
            raise ImportError("ollama not available. Install with: pip install ollama")
        
        try:
            ollama.list()
            print("Connected to Ollama successfully.")
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            print("Start Ollama server using: ollama serve")
        
        self._check_model()
    
    def _check_model(self):
        """Check if Ollama model is available"""
        try:
            models = ollama.list()["models"]
            names = [m["name"] for m in models]
            model_found = any(self.model_name in name or name.startswith(self.model_name.split(':')[0]) for name in names)
            
            if not model_found:
                print(f"Model '{self.model_name}' not found. Available models: {names}")
                print(f"\nTo download the model, run:")
                print(f" -> ollama pull {self.model_name}")
        except Exception as e:
            print(f"Error checking models: {e}")

    def generate(self, prompt, system_prompt=None, max_tokens=100, temperature=0.6):
        """Generate response from LLM"""
        return self._generate_ollama(prompt, system_prompt, max_tokens, temperature)
    
    def _generate_ollama(self, prompt, system_prompt=None, max_tokens=100, temperature=0.6):
        """Generate using Ollama"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        options = {
            "temperature": temperature,
            "num_predict": max_tokens,
        }

        try:
            result = ollama.chat(
                model=self.model_name,
                messages=messages,
                options=options
            )
            return result["message"]["content"]
        except Exception as e:
            error_str = str(e)
            if "not found" in error_str.lower() or "404" in error_str:
                print(f"\n[ERROR] Model '{self.model_name}' not found in Ollama.")
                print(f"Please download it using:")
                print(f"  ollama pull {self.model_name}")
            return f"Error generating response: {e}"


if __name__ == "__main__":
    print("Testing with Ollama (phi3)...")
    llm = LLMModule()
    print("LLM initialized.")
    response = llm.generate("Hello, how are you?")
    print(f"Response: {response}")
