import os
import json
import logging
from itertools import cycle
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class KeyManager:
    def __init__(self, keys: list[str]):
        if not keys:
            raise ValueError("No Groq API keys provided.")
        self.keys = cycle([k.strip() for k in keys])
        self.current_key = next(self.keys)
        self.key_count = len(keys)
        logging.info(f"KeyManager initialized with {self.key_count} keys")

    def switch_key(self):
        old_key = self.current_key[:6] + "..."
        self.current_key = next(self.keys)
        new_key = self.current_key[:6] + "..."
        logging.info(f"Switching API key from {old_key} to {new_key}")
        return self.current_key

# Load API keys
keys = os.getenv("GROQ_KEYS")
if not keys:
    raise ValueError("No GROQ_KEYS found in .env (set GROQ_KEYS=key1,key2,key3)")

key_manager = KeyManager(keys.split(","))

def get_model():
    return ChatGroq(
        api_key=key_manager.current_key.strip(),
        model="openai/gpt-oss-120b"
    )

with open("cybershield_template.json", "r", encoding="utf-8") as f:
    template_data = json.load(f)

prompt_template = template_data["template"]  # just grab the template string

def analyze_text(statement: str):
    errors = []
    attempts = 0
    max_attempts = key_manager.key_count

    formatted_prompt = prompt_template.replace("{statement_input}", statement)

    while attempts < max_attempts:
        current_key_prefix = key_manager.current_key[:6] + "..."
        logging.info(f"Attempt {attempts+1}/{max_attempts} with key {current_key_prefix}")

        model = get_model()
        try:
            response = model.invoke(formatted_prompt)
            if not response.content:
                raise ValueError("Empty response from model")
            return json.loads(response.content)

        except Exception as e:
            err_msg = str(e)
            logging.warning(f"Key {current_key_prefix} failed: {err_msg}")
            errors.append(err_msg)

            # immediate switch on rate-limit
            if "429" in err_msg or "Too Many Requests" in err_msg:
                logging.info(f"429 detected. Switching key immediately.")
                key_manager.switch_key()
                attempts += 1
                continue

            # other error -> still switch and retry
            key_manager.switch_key()
            attempts += 1

    raise RuntimeError("All keys failed:\n" + "\n".join(errors))


if __name__ == "__main__":
    sample_text = """
    Congress Hate Hindus, 
But they love Ghazwa-E-Hind

Do you agree..?

#gazwaehind #congress

"""
    result = analyze_text(sample_text)
    print(result["is_anti_india"])
    # print(json.dumps(result, indent=2, ensure_ascii=False))