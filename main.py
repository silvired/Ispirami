import os
from matcher import Matcher
from scraper import Scraper

def print_recipes(matcher_instance):
    matched_recipes = matcher_instance.get_matching_recipes()
    print(f"Found {len(matched_recipes)} matching recipes.")
    if len(matched_recipes) == 0:
        print("No recipes found.")
    else:
        print("Matching recipes:")
        for match in matched_recipes:
            print(f"  - {match}")

def main():
    # Check if Recipes folder exists
    recipes_folder = "Recipes"
    
    if not os.path.exists(recipes_folder):
        print("Recipes folder not found. Running scraper to download recipes...")
        scraper = Scraper()
        scraper.download_cookbook()
        print("Scraping completed.")
    else:
        print("Recipes folder found. Skipping scraper execution.")
    
    # Always run the matcher
    print("Running matcher...")
    matcher = Matcher()
    print_recipes(matcher)
    print("Matching completed.")

if __name__ == '__main__':
    main()
