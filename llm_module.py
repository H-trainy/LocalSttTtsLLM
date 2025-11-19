"""
LLM module using Ollama with Phi 3 model
Handles local LLM inference
"""
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ollama = None  # Set to None to avoid NameError
    print("Warning: ollama package not found. Install with: pip install ollama")


class LLMModule:
    def __init__(self, model_name='phi3:mini', use_cpu=False, num_gpu=0):
        """
        Initialize LLM module with Ollama
        
        Args:
            model_name: Name of the Ollama model (default: 'phi3:mini' - smaller, faster)
            use_cpu: Force CPU usage instead of GPU (default: False)
            num_gpu: Number of GPU layers to use (0 = CPU only, -1 = all GPU)
        """
        if not OLLAMA_AVAILABLE:
            raise ImportError("ollama package is required. Install with: pip install ollama")
        
        self.model_name = model_name
        self.use_cpu = use_cpu
        self.num_gpu = 0 if use_cpu else num_gpu
        
        # Try to initialize client (Ollama client can work without explicit initialization)
        try:
            # Test connection
            ollama.list()
            if self.use_cpu:
                print(f"Ollama connection successful. Using model: {self.model_name} (CPU mode)")
            else:
                print(f"Ollama connection successful. Using model: {self.model_name}")
        except Exception as e:
            print(f"Warning: Could not connect to Ollama: {e}")
            print("Make sure Ollama is running. Start it with: ollama serve")
        
        # Verify model is available
        self._check_model()
    
    def _check_model(self):
        """Check if the model is available, if not, provide instructions"""
        try:
            models = ollama.list()
            model_names = []
            if isinstance(models, dict) and 'models' in models:
                model_names = [model.get('name', '') for model in models['models']]
            elif isinstance(models, list):
                model_names = [model.get('name', '') for model in models]
            
            # Check if model name is in the list (handle variations like 'phi3:latest')
            model_found = any(self.model_name in name or name.startswith(self.model_name) for name in model_names)
            
            if not model_found and model_names:
                print(f"Warning: Model '{self.model_name}' not found in Ollama.")
                print(f"Available models: {model_names}")
                print(f"Please run: ollama pull {self.model_name}")
                print("Attempting to use the model anyway...")
        except Exception as e:
            print(f"Error checking Ollama models: {e}")
            print("Make sure Ollama is running. Start it with: ollama serve")
    
    def generate(self, prompt, system_prompt=None, max_tokens=128, temperature=0.6):
        """
        Generate response from LLM
        
        Args:
            prompt: User input prompt
            system_prompt: System prompt for context (optional)
            max_tokens: Maximum tokens to generate (default: 128 for faster responses)
            temperature: Sampling temperature (0.0 to 1.0, lower = faster)
        
        Returns:
            Generated response text
        """
        response = None  # Initialize to avoid scope issues
        try:
            messages = []
            
            # Add system prompt for intelligent responses
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            
            # Add user prompt (voice inputs are usually short, so no need to truncate)
            messages.append({
                'role': 'user',
                'content': prompt
            })
            
            # Configure options for speed optimization
            options = {
                'temperature': temperature,  # Lower = faster, more deterministic
                'num_predict': max_tokens,   # Shorter responses = faster
                'top_k': 20,                 # Limit vocabulary for speed
                'top_p': 0.9,                # Nucleus sampling for speed
            }
            
            # Force CPU if requested, or limit GPU layers
            if self.use_cpu or self.num_gpu == 0:
                options['num_gpu'] = 0
            elif self.num_gpu > 0:
                options['num_gpu'] = self.num_gpu
            
            # Generate response
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options=options
            )
            
            if response and 'message' in response and 'content' in response['message']:
                return response['message']['content']
            else:
                return "I received an unexpected response format from the model."
        
        except Exception as e:
            error_msg = str(e).lower()
            
            # Handle memory errors with helpful suggestions
            if 'memory' in error_msg or 'gpu' in error_msg or '500' in str(e):
                print(f"\n[WARNING] Memory/GPU error detected. Trying smaller model or CPU mode...")
                # Try to use a smaller model or CPU
                try:
                    # Try with CPU
                    print("Attempting with CPU mode...")
                    options = {
                        'temperature': temperature,
                        'num_predict': max_tokens,
                        'num_gpu': 0,  # Force CPU
                        'top_k': 20,   # Speed optimization
                        'top_p': 0.9   # Speed optimization
                    }
                    response = ollama.chat(
                        model=self.model_name,
                        messages=messages,
                        options=options
                    )
                    print("[OK] Successfully using CPU mode")
                    if response and 'message' in response and 'content' in response['message']:
                        return response['message']['content']
                    else:
                        return "I received an unexpected response format from the model."
                except Exception as e2:
                    print(f"\n[ERROR] Still failing. Trying to auto-switch to tinyllama...")
                    # Try to automatically switch to tinyllama
                    try:
                        if not OLLAMA_AVAILABLE or ollama is None:
                            raise ImportError("Ollama not available")
                        models = ollama.list()
                        model_names = []
                        if isinstance(models, dict) and 'models' in models:
                            model_names = [model.get('name', '') for model in models['models']]
                        elif isinstance(models, list):
                            model_names = [model.get('name', '') for model in models]
                        
                        # Check if tinyllama is available
                        tinyllama_available = any('tinyllama' in name for name in model_names)
                        
                        if tinyllama_available:
                            print("Switching to tinyllama (smallest model)...")
                            self.model_name = 'tinyllama'
                            options = {
                                'temperature': temperature,
                                'num_predict': max_tokens,
                                'num_gpu': 0,  # Force CPU
                                'top_k': 20,   # Speed optimization
                                'top_p': 0.9   # Speed optimization
                            }
                            response = ollama.chat(
                                model='tinyllama',
                                messages=messages,
                                options=options
                            )
                            print("[OK] Successfully using tinyllama")
                            if response and 'message' in response and 'content' in response['message']:
                                return response['message']['content']
                            else:
                                return "I received an unexpected response format from the model."
                    except:
                        pass
                    
                    print(f"\n[ERROR] All attempts failed. Suggestions:")
                    print("1. Pull smallest model: ollama pull tinyllama")
                    print("2. Or use: ollama pull phi3:mini")
                    print("3. Check available RAM/VRAM")
                    print("4. Close other applications using memory")
                    return f"I apologize, but I'm having memory issues. Please run 'ollama pull tinyllama' and restart. Error: {e}"
            
            # Other errors
            error_msg = f"Error generating response: {e}"
            print(error_msg)
            return f"I apologize, but I encountered an error: {error_msg}. Please make sure Ollama is running and the model is available."
    
    def set_model(self, model_name):
        """
        Change the LLM model
        
        Args:
            model_name: Name of the Ollama model
        """
        self.model_name = model_name
        self._check_model()


if __name__ == "__main__":
    # Test the LLM module
    llm = LLMModule(model_name='phi3')
    print("LLM module initialized successfully!")
    # Test generation
    response = llm.generate("Hello, how are you?")
    print(f"Test response: {response}")

