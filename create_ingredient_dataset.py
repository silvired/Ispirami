import json
import random
import pandas as pd
import os
from pathlib import Path

def create_ingredient_dataset():
    """
    Create a dataset of randomly selected ingredients from recipe files.
    """
    # Path to recipes folder
    recipes_folder = Path("recipes_1")
    
    # Get list of all recipe files
    recipe_files = list(recipes_folder.glob("*.json"))
    
    if not recipe_files:
        print("No recipe files found in recipes_1 folder")
        return
    
    print(f"Found {len(recipe_files)} recipe files")
    
    # Create empty dataframe with one column
    df = pd.DataFrame(columns=['full_ingredient'])
    
    # List to store ingredients
    ingredients_list = []
    
    # Do 200 iterations
    for i in range(200):
        # Randomly select a recipe file
        random_recipe_file = random.choice(recipe_files)
        
        try:
            # Read the recipe file
            with open(random_recipe_file, 'r', encoding='utf-8') as f:
                recipe_data = json.load(f)
            
            # Get ingredients list
            ingredients = recipe_data.get('ingredients', [])
            
            if ingredients:
                # Randomly select one ingredient
                random_ingredient = random.choice(ingredients)
                ingredients_list.append(random_ingredient)
                
                if (i + 1) % 50 == 0:
                    print(f"Processed {i + 1} iterations...")
            else:
                print(f"Warning: No ingredients found in {random_recipe_file.name}")
                
        except Exception as e:
            print(f"Error reading {random_recipe_file.name}: {e}")
            continue
    
    # Create dataframe from the ingredients list
    df = pd.DataFrame(ingredients_list, columns=['full_ingredient'])
    
    print(f"Created dataset with {len(df)} ingredients")
    
    # Save to CSV
    output_file = "random_ingredients.csv"
    df.to_csv(output_file, index=False)
    print(f"Dataset saved to {output_file}")
    
    # Display first few rows
    print("\nFirst 10 ingredients:")
    print(df.head(10))
    
    return df

if __name__ == "__main__":
    create_ingredient_dataset() 