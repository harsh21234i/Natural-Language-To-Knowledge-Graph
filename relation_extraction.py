from transformers import pipeline

# Load REBEL model
rebel_pipeline = pipeline("text2text-generation", model="Babelscape/rebel-large")

def extract_relationships(text):
    results = rebel_pipeline(text)
    triplets = []
    for result in results:
        triplets.append(result["generated_text"])
    return triplets