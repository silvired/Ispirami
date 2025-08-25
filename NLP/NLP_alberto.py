import csv
import sys
import os

# For now, we'll create a simplified analyze_ingredient function
# Later, this can be connected to the actual Alberto model
def analyze_ingredient(ingredient_text):
    """
    Simplified ingredient analysis function
    This is a placeholder that will be replaced with the actual Alberto model integration
    
    Args:
        ingredient_text (str): The ingredient text to analyze
        
    Returns:
        dict: Dictionary containing tokenization results
    """
    # Simple tokenization by splitting on spaces and common separators
    tokens = []
    
    # Split on common separators
    parts = ingredient_text.replace(':', ' : ').replace(',', ' , ').split()
    
    for part in parts:
        if part.strip():
            tokens.append(part.strip())
    
    return {
        'tokens': tokens,
        'text': ingredient_text
    }


def write_ingredients_to_csv(ingredients, recipe_title, csv_writer):
    """
    Write ingredient tokens to CSV with columns: recipe_title, ingredient_number, seq, token_name, pos, dep
    """
    for i, ingredient in enumerate(ingredients, 1):
        # Use simplified analyze_ingredient function
        result = analyze_ingredient(ingredient)
        
        # Write tokens to CSV
        for seq, token in enumerate(result['tokens'], 1):
            # For now, we'll use placeholder values for POS and dep since Alberto doesn't provide them directly
            # You might want to implement a more sophisticated approach later
            csv_writer.writerow([recipe_title, i, seq, token, 'UNKNOWN', 'UNKNOWN'])


def analyze_token_pos(token):
    """
    Basic POS analysis based on token characteristics
    """
    # Remove BERT subword markers
    clean_token = token.replace('##', '')
    
    # Check if it's a number
    if clean_token.replace(',', '').replace('.', '').replace('%', '').isdigit():
        return 'NUM'
    
    # Check if it's punctuation
    if clean_token in [':', '(', ')', ',', '.', '%']:
        return 'PUNCT'
    
    # Check if it's a unit of measurement
    if clean_token.lower() in ['g', 'kg', 'ml', 'l', 'pz', 'qb']:
        return 'NOUN'
    
    # Check if it's likely a proper noun (starts with capital letter)
    if clean_token and clean_token[0].isupper():
        return 'PROPN'
    
    # Default to noun for other tokens
    return 'NOUN'


def analyze_token_dependency(token, seq, all_tokens):
    """
    Basic dependency analysis based on token position and characteristics
    """
    clean_token = token.replace('##', '')
    
    # First token is usually the root
    if seq == 1:
        return 'ROOT'
    
    # Colon is always punctuation
    if clean_token == ':':
        return 'punct'
    
    # Numbers after colon are usually related to quantity
    if seq > 2 and clean_token.replace(',', '').replace('.', '').replace('%', '').isdigit():
        return 'nummod'
    
    # Units after numbers
    if seq > 3 and clean_token.lower() in ['g', 'kg', 'ml', 'l', 'pz']:
        return 'nmod'
    
    # Default dependency
    return 'dep'


def tokenize_ingredients(ingredients, recipe_title, csv_writer):
    """
    Tokenize and analyze ingredients using simplified analysis and save to CSV
    Uses natural language format: "ingredient_name: quantity"
    """
    print(f"\n=== RECIPE: {recipe_title} ===")
    print("\n=== INGREDIENT TOKEN ANALYSIS ===")
    
    for i, ingredient in enumerate(ingredients, 1):
        print(f"\nIngredient {i}: {ingredient}")
        
        # Split the natural language ingredient to show the components
        if ": " in ingredient:
            name_part, quantity_part = ingredient.split(": ", 1)
            print(f"  Name: '{name_part}'")
            print(f"  Quantity: '{quantity_part}'")
        
        # Use simplified analyze_ingredient function
        result = analyze_ingredient(ingredient)
        print(f"  Tokens: {len(result['tokens'])}")
        
        for token in result['tokens']:
            print(f"    {token}")
    
    print("\n" + "="*50)
    
    # Write to CSV
    write_ingredients_to_csv(ingredients, recipe_title, csv_writer)


def process_ingredient(full_ingredient):
    """
    Main function to process a single ingredient and return tokenization
    This function will be called by the scraper with a full_ingredient string
    
    Args:
        full_ingredient (str): The ingredient string in format "ingredient_name: quantity"
        
    Returns:
        dict: Dictionary containing tokenization results
    """
    # Use simplified analyze_ingredient function
    result = analyze_ingredient(full_ingredient)
    
    # Return the tokenization result
    return {
        'original_ingredient': full_ingredient,
        'tokens': result['tokens'],
        'token_count': len(result['tokens'])
    } 