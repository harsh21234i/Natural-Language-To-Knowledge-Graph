import cohere
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Initialize Cohere client
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(COHERE_API_KEY)

def generate_summary(text, max_tokens=150):
    """
    Generate a summary of the input text using Cohere's summarization model.
    """
    response = co.summarize(
        text=text,
        model="summarize-xlarge",  # Use the largest summarization model
        length="short",           # Options: 'short', 'medium', 'long'
        format="paragraph",       # Output format: 'paragraph' or 'bullets'
        extractiveness="high"     # How close the summary is to the original text
    )
    return response.summary