import os
import json
import logging
from itertools import cycle
import google.generativeai as genai
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class KeyManager:
    def __init__(self, keys: list[str]):
        if not keys:
            raise ValueError("No Gemini API keys provided.")
        # Strip whitespace from keys when initializing
        self.keys = cycle([k.strip() for k in keys])
        self.current_key = next(self.keys)
        self.key_count = len(keys)
        logging.info(f"KeyManager initialized with {self.key_count} keys")

    def switch_key(self):
        old_key = self.current_key[:6] + "..." # Log partial key for security
        self.current_key = next(self.keys)
        new_key = self.current_key[:6] + "..."
        logging.info(f"Switching API key from {old_key} to {new_key}")
        return self.current_key

# Load multiple keys from .env
# Example in .env: GEMINI_KEYS=key1,key2,key3
keys = os.getenv("GEMINI_KEYS")
if not keys:
    raise ValueError("No GEMINI_KEYS found. Set GEMINI_KEYS=key1,key2,key3 in .env")

key_manager = KeyManager(keys.split(","))

def get_model():
    """Get a configured Gemini model instance with the current API key."""
    genai.configure(api_key=key_manager.current_key.strip())
    return genai.GenerativeModel('gemini-2.0-flash-lite')

class SentimentAnalysis(BaseModel):
    is_anti_india: bool = Field(description="Whether the text has anti-India sentiment (True/False)")
    threat_score: int = Field(description="A score from 0-100 indicating the level of threat")
    justification: str = Field(description="Explanation for the assigned threat score")

parser = PydanticOutputParser(pydantic_object=SentimentAnalysis)

prompt_template = """
You are analyzing a social media post for anti-India sentiment. 
Do not flag ordinary criticism, humor, or sarcasm. 
Only consider as anti-India if the text explicitly supports:
- violence against India or its people,
- separatist movements seeking to break India apart,
- armed revolt, terrorism, or violent protest,
- direct hostility against India's sovereignty.

Ignore generic criticism of policies, leaders, or institutions.
Ignore sarcasm or satire unless it directly incites hostility.

Output strictly in JSON:
{format_instructions}

Text to analyze:
{text}
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

def analyze_text(text: str):
    errors = []
    attempts = 0
    max_attempts = key_manager.key_count
    
    # Format the prompt template
    formatted_prompt = prompt.format(text=text, format_instructions=parser.get_format_instructions())
    
    while attempts < max_attempts:
        current_key_prefix = key_manager.current_key[:6] + "..."
        logging.info(f"Attempt {attempts + 1}/{max_attempts} using key {current_key_prefix}")
        
        model = get_model()
        try:
            # Make direct API call
            response = model.generate_content(formatted_prompt)
            
            if not response.text:
                raise ValueError("Empty response from model")
                
            # Parse the JSON response
            result = parser.parse(response.text)
            logging.info(f"Successfully analyzed text with key {current_key_prefix}")
            return result
            
        except Exception as e:
            error_msg = f"Key {current_key_prefix} failed: {str(e)}"
            error_str = str(e).lower()
            
            # Check for quota-related errors specifically
            if "quota" in error_str or "429" in error_str or "rate limit" in error_str:
                logging.warning(f"Quota exceeded for key {current_key_prefix}, switching to next key")
            else:
                logging.error(error_msg)
            
            errors.append(error_msg)
            key_manager.switch_key()
            attempts += 1
    
    error_summary = "\n".join(errors)
    logging.error(f"All Gemini API keys failed:\n{error_summary}")
    raise RuntimeError("All Gemini API keys failed.\n" + error_summary)

if __name__ == "__main__":
    sample_text = "#boycottindia Kashmir banega pakistan ka hissa"
    result = analyze_text(sample_text)
    print(result)