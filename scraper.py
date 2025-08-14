import json
import os
import re
import sys
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

sys.path.append(os.path.abspath(".."))
sys.path.append(os.path.abspath("test NLP"))

from model_recipe import ModelRecipe
from test_nlp import nlp

class Scraper:
    def __init__(self):
        self.cookbook_url = "https://www.giallozafferano.it/ricette-cat"
        self.folder_recipes = "Recipes"
        # Ensure the Recipes directory exists
        if not os.path.exists(self.folder_recipes):
            os.makedirs(self.folder_recipes)

    def get_recipes_links(self, page_url):
        """
        Extract recipe links from a page listing recipes
        """
        response = requests.get(page_url)
        soup = BeautifulSoup(response.text, "html.parser")
        recipe_links = []
        
        recipe_title_elements = soup.find_all(class_="gz-title")
        
        if recipe_title_elements:
            for elem in recipe_title_elements:
                # Find the <a> element inside the <h2> element
                link_elem = elem.find('a')
                if link_elem:
                    href = link_elem.get('href')
                    
                    if href and not href.startswith('#') and not href.startswith('javascript:'):
                        # Convert relative URL to absolute URL
                        if href.startswith('/'):
                            href = 'https://www.giallozafferano.it' + href
                        
                        # Clean up URL by removing anchor fragments
                        if '#' in href:
                            href = href.split('#')[0]
                        
                        recipe_links.append(href)
        
        return recipe_links

    def count_total_pages(self):
        number_of_pages = 0
        response = requests.get(self.cookbook_url)
        soup = BeautifulSoup(response.text, "html.parser")
        
        pagination_tags = soup.find_all(attrs={"class": "disabled total-pages"})
        
        for tag in pagination_tags:
            number_of_pages = int(tag.text)
        
        return number_of_pages

    def download_cookbook(self):
        # Limit to 1 page for testing purposes
        total_pages = min(1, self.count_total_pages() + 1)
        total_recipes_processed = 0
        total_recipes_saved = 0
        
        for page_number in range(1, total_pages + 1):
            # New URL structure: /page2/ instead of /page/2
            if page_number == 1:
                page_url = self.cookbook_url
            else:
                page_url = self.cookbook_url + '/page' + str(page_number) + '/'
            
            # Get recipe links from the page
            recipe_links = self.get_recipes_links(page_url)
            
            for i, recipe_link in enumerate(recipe_links):
                # Process all recipe links found (we know they're correct from gz-title elements)
                total_recipes_processed += 1
                if self.process_recipe(recipe_link):
                    total_recipes_saved += 1
                
        print(f"Total recipes processed: {total_recipes_processed}")
        print(f"Total recipes saved: {total_recipes_saved}")
        print("Scraping completed.")

    def process_recipe(self, link_recipe_to_download):
        soup = download_page(link_recipe_to_download)
        ingredients = find_ingredients(soup)
        title = find_title(soup)
        if ingredients:
            categories = find_category(soup)
            recipe_features = find_recipe_features(soup)
            recipe_nutritional_values = find_recipe_nutritional_values(soup)

            # Tokenize and analyze ingredients
            tokenize_ingredients(ingredients)
            
            return True
        return False

    def calculate_file_path(self, title):
        compact_name = title.replace(" ", "_").lower()
        return self.folder_recipes + "/" + compact_name + ".json"

    def extract_recipes_from_category(self, category_url):
        """Extract individual recipe links from a category page"""
        recipe_links = []
        response = requests.get(category_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Look for individual recipe links on the category page
        # Try different selectors for recipe links
        recipe_selectors = [
            'a[href*="/ricette/"]',  # Links containing /ricette/
            'a[href*=".html"]',      # Links ending with .html
            '.recipe-card a',        # Recipe card links
            '.recipe-item a',        # Recipe item links
            'h2 a',                  # Links within h2 tags
            'h3 a'                   # Links within h3 tags
        ]
        
        for selector in recipe_selectors:
            links = soup.select(selector)
            if links:
                for link in links:
                    href = link.get('href')
                    if href and not href.startswith('#'):
                        # Convert relative URL to absolute URL
                        if href.startswith('/'):
                            href = 'https://www.giallozafferano.it' + href
                        recipe_links.append(href)
                break  # Use the first selector that finds links
        
        return recipe_links

def find_title(soup):
    title_recipe = ""
    # Try multiple selectors for the new structure
    selectors = [
        'h1',  # Main recipe title
        '.recipe-title',  # Common recipe title class
        'h2',  # Alternative title
        'title'  # Page title as fallback
    ]
    
    for selector in selectors:
        title_elements = soup.find_all(selector)
        for title in title_elements:
            if title.text.strip():
                title_recipe = title.text.strip()
                break
        if title_recipe:
            break
    
    return title_recipe


def find_ingredients(soup):
    all_ingredients = []
    
    ingredient_tags = soup.find_all(class_="gz-ingredient")
    for i, tag in enumerate(ingredient_tags, 1):
        name_elem = tag.find('a')
        ingredient_name = name_elem.get_text()
        quantity_elem = tag.find('span')
        ingredient_quantity_raw = quantity_elem.get_text()
        ingredient_quantity = " ".join(ingredient_quantity_raw.replace('\t', '').split('\n')).strip()
        full_ingredient = f"{ingredient_name} {ingredient_quantity}"
        
        all_ingredients.append(full_ingredient)
    
    return all_ingredients


def find_category(soup):
    cat_tag = soup.find(class_="gz-breadcrumb")
    categories = cat_tag.get_text().split('\n')
    categories = [cat for cat in categories if cat != '']
    
    return categories


def find_recipe_features(soup):
    recipe_features = {}
    recipes_data_tags = soup.find_all(class_="gz-name-featured-data")
    for tag in recipes_data_tags:
        text = tag.get_text()
        if ": " in text:
            feature, value = text.split(': ')
            recipe_features[feature] = value
    
    return recipe_features


def find_recipe_nutritional_values(soup):
    recipe_nutritional_values = {}
    macros_tags = soup.find_all(class_="gz-list-macros-name")
    unit_tags = soup.find_all(class_="gz-list-macros-unit")
    value_tags = soup.find_all(class_="gz-list-macros-value")
    macros = [tag.get_text() for tag in macros_tags]
    macros_amended = [macro.lstrip() for macro in macros]
    value = [float(tag.get_text().replace(',','.')) for tag in value_tags]

    for i in range(len(macros_amended)):
        recipe_nutritional_values[macros_amended[i]] = value[i]
    
    return recipe_nutritional_values


def download_page(link_to_download):
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            response = requests.get(link_to_download, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            return soup
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError) as e:
            if attempt < max_retries - 1:
                import time
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

def tokenize_ingredients(ingredients):
    """
    Tokenize and analyze ingredients using NLP
    """
    print("\n=== INGREDIENT TOKEN ANALYSIS ===")
    
    for i, ingredient in enumerate(ingredients, 1):
        print(f"\nIngredient {i}: {ingredient}")
        
        # Use NLP to analyze the ingredient
        doc = nlp(ingredient)
        print(f"  Tokens: {len(doc)}")
        
        for token in doc:
            print(f"    {token.text:<15} {token.pos_:<10} {token.dep_:<10}")
    
    print("\n" + "="*50)


# Main execution block
if __name__ == "__main__":
    print("Starting the scraper...")
    scraper = Scraper()
    scraper.download_cookbook()



