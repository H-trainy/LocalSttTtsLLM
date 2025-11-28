"""
Intent Analyzer Module
Analyzes transcribed text to extract:
- Summary (1-2 lines)
- Keywords
- Intent identification
"""

from llm_module import LLMModule
import json
import re


class IntentAnalyzer:
    def __init__(self, llm_model='sarvam-m', api_key=None):
        """
        Initialize Intent Analyzer
        
        Args:
            llm_model: Sarvam AI model name (default: 'sarvam-m' - multilingual model)
            api_key: Sarvam AI API key (if None, reads from SARVAM_API_KEY env var)
        """
        self.llm = LLMModule(model_name=llm_model, api_key=api_key)
        
        # System prompts for analysis in different languages (focus on intent only - short and specific)
        self.analysis_prompts = {
            'hindi': """आप एक बुद्धिमान विश्लेषक हैं। दिए गए पाठ का विश्लेषण करें और उपयोगकर्ता का इरादा पहचानें।
INTENT: केवल 2-3 शब्दों में इरादा बताएं (अंग्रेजी में)। उदाहरण: "power cut", "complaint", "inquiry", "request"

उत्तर केवल INTENT: के साथ दें, कोई अतिरिक्त व्याख्या न करें।""",
            
            'english': """You are an intelligent analyst. Analyze the given text and identify the user's intent.
INTENT: Provide intent in only 2-3 words (in English). Examples: "power cut", "complaint", "inquiry", "request"

Provide the answer only with INTENT:, no additional explanation.""",
            
            'urdu': """آپ ایک ذہین تجزیہ کار ہیں۔ دیے گئے متن کا تجزیہ کریں اور صارف کا ارادہ پہچانیں۔
INTENT: صرف 2-3 الفاظ میں ارادہ بتائیں (انگریزی میں)۔ مثال: "power cut", "complaint", "inquiry"

جواب صرف INTENT: کے ساتھ دیں، کوئی اضافی وضاحت نہ کریں۔""",
            
            'telugu': """మీరు ఒక తెలివైన విశ్లేషకుడు. ఇచ్చిన టెక్స్ట్‌ను విశ్లేషించి వినియోగదారు ఉద్దేశాన్ని గుర్తించండి.
INTENT: కేవలం 2-3 పదాలలో ఉద్దేశాన్ని అందించండి (ఇంగ్లీష్‌లో). ఉదాహరణ: "power cut", "complaint", "inquiry"

సమాధానాన్ని INTENT: తో మాత్రమే ఇవ్వండి, అదనపు వివరణ ఇవ్వవద్దు."""
        }
    
    def analyze(self, text, language='english'):
        """
        Analyze transcribed text to extract intent only
        
        Args:
            text: Transcribed text to analyze
            language: Language of the text ('hindi', 'english', 'urdu', 'telugu')
        
        Returns:
            Dictionary with 'intent'
        """
        if not text or not text.strip():
            return {
                'intent': ''
            }
        
        # Use English system prompt for intent (always in English, 2-3 words)
        system_prompt = """You are an intent classifier. Your task is to identify the user's intent from the given text and provide it in exactly 2-3 words in English. 
Examples of correct intents:
- "power cut" (for power/electricity issues)
- "complaint" (for complaints)
- "bill inquiry" (for bill questions)
- "connection request" (for new connections)
- "payment issue" (for payment problems)
- "service request" (for service requests)

Provide ONLY the intent in 2-3 words, nothing else."""
        
        # Create analysis prompt (intent should be short, 2-3 words in English)
        analysis_prompt = f"Identify the user's intent from this text. Provide ONLY 2-3 words in English.\n\nText: {text}\n\nIntent (2-3 words only):"
        
        try:
            # Get LLM response
            response = self.llm.generate(
                prompt=analysis_prompt,
                system_prompt=system_prompt,
                max_tokens=20,  # Very short - only need 2-3 words
                temperature=0.2  # Very low temperature for consistent output
            )
            
            # Parse the response
            parsed_result = self._parse_response(response)
            return parsed_result
            
        except Exception as e:
            print(f"[ERROR] Intent analysis failed: {e}")
            return {
                'intent': 'unknown'
            }
    
    def _parse_response(self, response):
        """
        Parse LLM response to extract intent only (2-3 words max)
        
        Args:
            response: Raw LLM response string
        
        Returns:
            Dictionary with parsed results
        """
        result = {
            'intent': ''
        }
        
        if not response:
            return result
        
        # Clean the response
        response = response.strip()
        
        # Remove common prefixes
        response = re.sub(r'^(intent|intent:|the intent is|user intent|intent is)[:\s]*', '', response, flags=re.IGNORECASE)
        response = response.strip()
        
        # Remove quotes
        response = response.strip('"\'')
        
        # Remove any trailing punctuation
        response = re.sub(r'[.,;:!?]+$', '', response)
        
        # Split into words and clean each word
        words = []
        for word in response.split():
            # Remove special characters but keep hyphens (for "power-cut" -> "power cut")
            word = re.sub(r'[^\w-]', '', word)
            if word and len(word) > 0:
                words.append(word.lower())
        
        # Take only first 2-3 words
        if len(words) > 3:
            words = words[:3]
        
        result['intent'] = ' '.join(words) if words else 'unknown'
        
        return result
    
    def format_analysis(self, analysis_result):
        """
        Format analysis result as a readable string
        
        Args:
            analysis_result: Dictionary with 'intent'
        
        Returns:
            Formatted string
        """
        output = []
        
        if analysis_result.get('intent'):
            output.append(f"INTENT: {analysis_result['intent']}")
        
        return '\n'.join(output)


if __name__ == "__main__":
    # Test the intent analyzer
    print("Testing Intent Analyzer...")
    analyzer = IntentAnalyzer()
    
    # Test with Hindi text
    test_text = "Hi Tech City mein subah se current nahi hai, current kab tak aayega bhaiya?"
    print(f"\nInput Text: {test_text}")
    
    result = analyzer.analyze(test_text, language='hindi')
    print("\nAnalysis Result:")
    print(analyzer.format_analysis(result))
    print(f"\nDetailed Result: {result}")

