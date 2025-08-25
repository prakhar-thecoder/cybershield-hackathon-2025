import os
from itertools import cycle
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class KeyManager:
    def __init__(self, keys: list[str]):
        if not keys:
            raise ValueError("No Gemini API keys provided.")
        self.keys = cycle(keys)
        self.current_key = next(self.keys)

    def switch_key(self):
        self.current_key = next(self.keys)
        return self.current_key

# Load multiple keys from .env
# Example in .env: GEMINI_KEYS=key1,key2,key3
keys = os.getenv("GEMINI_KEYS")
if not keys:
    raise ValueError("No GEMINI_KEYS found. Set GEMINI_KEYS=key1,key2,key3 in .env")

key_manager = KeyManager(keys.split(","))

def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        google_api_key=key_manager.current_key.strip()
    )

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
    for _ in range(len(keys.split(","))):  # try each key once
        llm = get_llm()
        chain = prompt | llm | parser
        try:
            return chain.invoke({"text": text})
        except Exception as e:
            errors.append(f"Key {key_manager.current_key} failed: {e}")
            key_manager.switch_key()
    raise RuntimeError("All Gemini API keys failed.\n" + "\n".join(errors))

if __name__ == "__main__":
    sample_text = "#boycottindia Kashmir banega pakistan ka hissa"
    result = analyze_text(sample_text)
    print(result)