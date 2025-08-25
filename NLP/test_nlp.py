from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import torch

print("Starting NLP analysis...")

# Load a proper Italian model with POS tagging and dependency parsing
# Using a model that's specifically designed for Italian language tasks
try:
    print("Loading Italian model with POS and dependency analysis...")
    
    # For POS tagging, we'll use a model specifically trained for that
    pos_model_name = "dbmdz/bert-base-italian-xxl-cased"
    pos_tokenizer = AutoTokenizer.from_pretrained(pos_model_name)
    pos_model = AutoModelForTokenClassification.from_pretrained(pos_model_name)
    
    # For NER (Named Entity Recognition)
    ner_pipeline = pipeline("ner", model=pos_model, tokenizer=pos_tokenizer, aggregation_strategy="simple")
    
    # For basic tokenization
    tokenizer = pos_tokenizer
    
    print("Italian model loaded successfully!")
    print("Note: This model provides tokenization and NER. For full POS/dependency analysis,")
    print("consider using spaCy with it_core_news_lg or a specialized Italian NLP pipeline.")
    
except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)

def analyze_ingredient(ingredient_text):
    """Analyze an ingredient text using the Italian model"""
    # Tokenize the text
    tokens = tokenizer.tokenize(ingredient_text)
    
    # Get NER results
    ner_results = ner_pipeline(ingredient_text)
    
    # For now, we'll provide basic POS-like analysis based on token patterns
    # This is a simplified approach - for production use, consider spaCy or specialized models
    basic_pos = analyze_basic_pos(tokens)
    
    return {
        'tokens': tokens,
        'ner': ner_results,
        'basic_pos': basic_pos,
        'text': ingredient_text
    }

def analyze_basic_pos(tokens):
    """Basic POS analysis based on token patterns and Italian language rules"""
    pos_results = []
    
    for token in tokens:
        # Basic pattern matching for Italian cooking terminology
        if token.isdigit():
            pos_results.append(('NUM', 'number'))
        elif token in [':', '(', ')', ',', '.']:
            pos_results.append(('PUNCT', 'punctuation'))
        elif token.startswith('##'):
            pos_results.append(('SUFFIX', 'subword_suffix'))
        elif token.lower() in ['di', 'da', 'a', 'in', 'con', 'per', 'tra', 'fra']:
            pos_results.append(('PREP', 'preposition'))
        elif token.lower() in ['il', 'la', 'lo', 'i', 'gli', 'le', 'un', 'una', 'uno']:
            pos_results.append(('DET', 'determiner'))
        elif token.lower() in ['e', 'o', 'ma', 'però', 'quindi']:
            pos_results.append(('CONJ', 'conjunction'))
        elif token.lower() in ['q', 'b']:
            pos_results.append(('ABBR', 'abbreviation'))
        elif token.lower() in ['g', 'kg', 'ml', 'l', 'pz', 'cucchiaio', 'cucchiaino']:
            pos_results.append(('UNIT', 'unit_of_measure'))
        else:
            # Default to noun for most Italian ingredient words
            pos_results.append(('NOUN', 'noun'))
    
    return pos_results

# Test the function
if __name__ == "__main__":
    text = "uova 1 media, pepe q.b., sale un pizzico"
    print(f"Analyzing text: '{text}'")

    result = analyze_ingredient(text)
    print(f"Document created with {len(result['tokens'])} tokens")

    print("\n=== TOKEN ANALYSIS ===")
    for i, (token, (pos, description)) in enumerate(zip(result['tokens'], result['basic_pos'])):
        print(f"Token {i+1}: {token:<15} POS: {pos:<8} ({description})")

    print("\n=== NAMED ENTITIES ===")
    if result['ner']:
        for ent in result['ner']:
            print(f"Entity: {ent['word']:<20} Label: {ent['entity_group']:<15} Score: {ent['score']:.3f}")
    else:
        print("No named entities found in this text.")

    print("\n=== ANALYSIS COMPLETE ===")
    print("\nRecommendation: For production use with full POS and dependency analysis,")
    print("consider using spaCy with the it_core_news_lg model:")
    print("python -m spacy download it_core_news_lg")