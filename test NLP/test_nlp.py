import spacy

print("Starting NLP analysis...")

# Load the Italian model
# You might need to download it first with: python -m spacy download it_core_news_sm
try:
    print("Loading Italian model...")
    nlp = spacy.load("it_core_news_sm")
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)

def analyze_ingredient(ingredient_text):
    """Analyze an ingredient text and return the document"""
    doc = nlp(ingredient_text)
    return doc

# Test the function
if __name__ == "__main__":
    text = "uova 1 media, pepe q.b., sale un pizzico"
    print(f"Analyzing text: '{text}'")

    doc = nlp(text)
    print(f"Document created with {len(doc)} tokens")

    print("\n=== TOKEN ANALYSIS ===")
    for token in doc:
        print(f"{token.text:<10} {token.pos_:<10} {token.dep_:<10}")

    print("\n=== NAMED ENTITIES ===")
    # Example of how you might start to extract entities
    # This will be more effective after training a custom NER model
    if doc.ents:
        for ent in doc.ents:
            print(f"Entity: {ent.text:<20} Label: {ent.label_}")
    else:
        print("No named entities found in this text.")

    print("\n=== ANALYSIS COMPLETE ===")