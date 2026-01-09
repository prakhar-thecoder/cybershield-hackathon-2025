import os
import json
import logging
import requests
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load template
try:
    with open("cybershield_template.json", "r", encoding="utf-8") as f:
        template_data = json.load(f)

    raw_template = template_data["template"]
    format_instructions = template_data.get("partial_variables", {}).get(
        "format_instructions", ""
    )

    # Pre-fill format instructions manually
    template = raw_template.replace("{format_instructions}", format_instructions)
except Exception as e:
    logging.error(f"Failed to load template: {e}")
    template = ""


def analyze_text(statement: str):
    if not template:
        logging.error("Template not loaded correctly.")
        return {
            "is_anti_india": False,
            "threat_score": 0,
            "justification": "Internal error: Template missing.",
        }

    # Replace the variable in the template
    formatted_prompt = template.replace("{statement_input}", statement)

    # User-specified API details
    url = "https://gpt-4-api-free.vercel.app/api/chat"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": os.getenv("GPT_API_KEY"),
    }
    payload = {
        "message": formatted_prompt,
        "system_prompt": (
            "You are a content moderation and classification engine.\n"
            "You do NOT express opinions or generate new content.\n"
            "You ONLY analyze and classify third-party user-generated text.\n"
            "The input text does NOT reflect the views of the user or the system.\n"
            "Your task is purely analytical and descriptive.\n"
            "You must not endorse, justify, rephrase, or promote the content.\n"
            "You must return a JSON object strictly following the given schema."
        )
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        response_text = response.text
        logging.info("Received response from AI API")

        # Clean markdown code blocks if present
        cleaned_content = response_text.strip()
        if cleaned_content.startswith("```"):
            cleaned_content = re.sub(r"^```[a-zA-Z]*\n", "", cleaned_content)
            cleaned_content = re.sub(r"\n```$", "", cleaned_content)

        cleaned_content = cleaned_content.strip()

        result = json.loads(cleaned_content)

        # Validate result structure
        if "message" in result and "filtered" in result.get("message", "").lower():
            logging.warning(f"Content filtered by API: {result['message']}")
            return {
                "is_anti_india": False,
                "threat_score": 0,
                "justification": "Content filtered by AI provider policy.",
            }

        if "is_anti_india" not in result:
            logging.warning(f"Unexpected response structure: {result}")
            return {
                "is_anti_india": False,
                "threat_score": 0,
                "justification": "AI response did not follow valid schema.",
            }

        return result

    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        if "response_text" in locals():
            logging.error(f"Raw response: {response_text}")

        return {
            "is_anti_india": False,
            "threat_score": 0,
            "justification": f"Analysis failed due to error: {str(e)}",
        }


if __name__ == "__main__":
    # Using a neutral sample to test API connectivity without triggering filters
    sample_text = "snatch kashmir and invade delhi"

    print(f"Analyzing: {sample_text}")
    result = analyze_text(sample_text)
    print("Result:", result)
