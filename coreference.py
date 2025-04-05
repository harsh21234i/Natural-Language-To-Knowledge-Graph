import stanza

# Initialize Stanza pipeline with default processors
nlp = stanza.Pipeline('en', processors={'tokenize': 'default'})  # Use 'default' tokenizer instead of 'spacy'

def resolve_coreferences(text):
    """
    Resolve coreferences in the input text using Stanza.
    """
    doc = nlp(text)
    resolved_text = ""
    for sentence in doc.sentences:
        for word in sentence.words:
            if word.parent.text == "-PRON-":  # Pronoun detected
                resolved_text += word.parent.head.text + " "
            else:
                resolved_text += word.text + " "
        resolved_text += "\n"
    return resolved_text.strip()