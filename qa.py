import cohere
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Initialize Cohere client
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(COHERE_API_KEY)

def answer_question(question, context):
    """
    Answer a question based on the provided context using Cohere's generate endpoint.
    """
    prompt = f"""
    Context: {context}
    Question: {question}
    Answer:
    """
    response = co.generate(
        model="command-xlarge-nightly",  # Use a large generative model
        prompt=prompt,
        max_tokens=50,                  # Limit the response length
        temperature=0.7,                # Control randomness (lower = more deterministic)
        stop_sequences=["\n"]           # Stop generating after a newline
    )
    return response.generations[0].text.strip()