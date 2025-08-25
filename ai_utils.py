import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Get the API key from the environment
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in the .env file.")

# Initialize the model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", google_api_key=GOOGLE_API_KEY)

class SentimentAnalysis(BaseModel):
    is_anti_india: bool = Field(description="Whether the text has anti-India sentiment (True/False)")
    threat_score: int = Field(description="A score from 0-100 indicating the level of threat")
    justification: str = Field(description="Explanation for the assigned threat score")

class BatchSentimentAnalysis(BaseModel):
    analyses: list[SentimentAnalysis] = Field(description="A list of sentiment analysis results for the batch of texts")

# Create a Pydantic parser
parser = PydanticOutputParser(pydantic_object=SentimentAnalysis)
batch_parser = PydanticOutputParser(pydantic_object=BatchSentimentAnalysis)

# Create a prompt template
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

batch_prompt_template = """
You are analyzing a batch of social media posts for anti-India sentiment. 
Do not flag ordinary criticism, humor, or sarcasm. 
Only consider as anti-India if the text explicitly supports:
- violence against India or its people,
- separatist movements seeking to break India apart,
- armed revolt, terrorism, or violent protest,
- direct hostility against India's sovereignty.

Ignore generic criticism of policies, leaders, or institutions.
Ignore sarcasm or satire unless it directly incites hostility.

Output strictly in JSON. For each post, provide a JSON object with the required fields. The final output should be a JSON object with a single key "analyses" that contains a list of these JSON objects.
{format_instructions}

Here are the posts to analyze, each in a numbered list:
{texts}
"""


prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

batch_prompt = PromptTemplate(
    template=batch_prompt_template,
    input_variables=["texts"],
    partial_variables={"format_instructions": batch_parser.get_format_instructions()}
)

def analyze_text(text: str):
    chain = prompt | llm | parser
    result = chain.invoke({"text": text})
    return result

def analyze_batch(texts: list[str]):
    formatted_texts = "\n".join([f"{i+1}. {text}" for i, text in enumerate(texts)])
    chain = batch_prompt | llm | batch_parser
    result = chain.invoke({"texts": formatted_texts})
    return result.analyses


if __name__ == "__main__":
    sample_text = "#boycottindia"
    analysis_result = analyze_text(sample_text)
    print(analysis_result)