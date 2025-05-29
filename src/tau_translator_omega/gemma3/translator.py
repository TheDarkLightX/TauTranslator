
"""
Gemma 3 Translator for TauTranslatorOmega
========================================

Uses Google's Gemma 3 model for enhanced Tau ↔ TCE translation.
"""

import torch
from pathlib import Path
from typing import Optional, Dict, Any

class Gemma3Translator:
    """Gemma 3 powered translator for Tau ↔ TCE."""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.loaded = False
        self.model_path = Path("models/gemma3")
        
    def load_model(self) -> bool:
        """Load Gemma 3 model."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            # Check if model exists
            config_file = self.model_path / "config.json"
            if not config_file.exists():
                print("❌ Gemma 3 model not found. Run setup_gemma3.py first.")
                return False
            
            import json
            with open(config_file) as f:
                config = json.load(f)
            
            model_name = config["model_name"]
            
            print("🔄 Loading Gemma 3...")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=str(self.model_path),
                trust_remote_code=True
            )
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                cache_dir=str(self.model_path),
                torch_dtype=torch.bfloat16,
                device_map="auto",
                trust_remote_code=True
            )
            
            self.loaded = True
            print("✅ Gemma 3 loaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load Gemma 3: {e}")
            return False
    
    def translate_tau_to_tce(self, tau_code: str) -> Optional[str]:
        """Translate Tau code to TCE using Gemma 3."""
        if not self.loaded:
            return None
        
        try:
            # Craft a specific prompt for Tau → TCE translation
            prompt = f"""You are an expert in formal languages and natural language. Convert this Tau Language code to clear, natural English description.

Tau Language code:
{tau_code}

Natural English description:"""
            
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=150,
                    temperature=0.3,  # Lower temperature for more consistent output
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Extract generated text
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            generated = full_response[len(prompt):].strip()
            
            # Clean up the response
            if generated:
                # Remove any trailing incomplete sentences
                sentences = generated.split('.')
                if len(sentences) > 1 and sentences[-1].strip() == '':
                    sentences = sentences[:-1]
                
                cleaned = '. '.join(sentences).strip()
                if cleaned and not cleaned.endswith('.'):
                    cleaned += '.'
                
                return cleaned
            
            return None
            
        except Exception as e:
            print(f"Gemma 3 translation error: {e}")
            return None
    
    def translate_tce_to_tau(self, tce_text: str) -> Optional[str]:
        """Translate TCE to Tau code using Gemma 3."""
        if not self.loaded:
            return None
        
        try:
            # Craft a specific prompt for TCE → Tau translation
            prompt = f"""You are an expert in formal languages. Convert this natural English description to Tau Language code.

Natural English description:
{tce_text}

Tau Language code:"""
            
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=100,
                    temperature=0.2,  # Very low temperature for code generation
                    do_sample=True,
                    top_p=0.8,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Extract generated text
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            generated = full_response[len(prompt):].strip()
            
            # Clean up the code response
            if generated:
                # Take only the first line of code (avoid hallucination)
                lines = generated.split('\n')
                code_line = lines[0].strip()
                
                # Basic validation - should contain Tau language patterns
                if any(pattern in code_line for pattern in [':=', '=', '&', '|', 'r ', 'sbf', 'always']):
                    return code_line
            
            return None
            
        except Exception as e:
            print(f"Gemma 3 translation error: {e}")
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        if not self.loaded:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "model_type": "gemma3",
            "capabilities": [
                "tau_to_tce_translation",
                "tce_to_tau_translation",
                "code_understanding",
                "instruction_following"
            ],
            "quality": "high"
        }

# Global instance
gemma3_translator = Gemma3Translator()
