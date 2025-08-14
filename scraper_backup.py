import json
import os
import re
import sys
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

sys.path.append(os.path.abspath(".."))

from model_recipe import ModelRecipe
from quantity_udm_parser import get_quantity_udm

debug = False

class Scraper:
    def __init__(self):
        self.cookbook_url = "https://www.giallozafferano.it/ricette-cat"
        self.folder_recipes = "Recipes"
        # Ensure the Recipes directory exists
        if not os.path.exists(self.folder_recipes):
            os.makedirs(self.folder_recipes)

    def download_cookbook(self):
        total_pages = self.count_total_pages() + 1
        total_recipes_processed = 0
        total_recipes_saved = 0
        for page_number in tqdm(range(1, total_pages), desc="pages…", ascii=False, ncols=75):
            print(f"\nProcessing page {page_number}/{total_pages-1}...")
            
            # Cautious strategy: Sleep for 5 minutes every 40 pages to avoid being blocked
            if page_number > 1 and page_number % 40 == 0:
                print(f"\n⚠️  Cautious pause: Sleeping for 5 minutes after processing {page_number} pages...")
                import time
                time.sleep(300)  # 5 minutes = 300 seconds
                print("Resuming scraping...")
            
            # New URL structure: /page2/ instead of /page/2
            if page_number == 1:
                link_list = self.cookbook_url
            else:
                link_list = self.cookbook_url + '/page' + str(page_number) + '/'
            if debug:
                print(f"Requesting URL: {link_list}")
            response = requests.get(link_list)
            soup = BeautifulSoup(response.text, "html.parser")
            page_recipes = 0
            # Look for individual recipe links on the main listing page
            # The main listing pages contain recipe cards with individual recipe links
            # Try to find the recipe cards and extract their links
            recipe_links = []
            
            # Method 1: Look for recipe cards with links
            recipe_cards = soup.find_all(['article', 'div'], class_=lambda x: x and ('recipe' in x.lower() or 'card' in x.lower()))
            for card in recipe_cards:
                link_elem = card.find('a')
                if link_elem and link_elem.get('href'):
                    href = link_elem.get('href')
                    if href and not href.startswith('#'):
                        if href.startswith('/'):
                            href = 'https://www.giallozafferano.it' + href
                        recipe_links.append(href)
            
            # Method 2: If no recipe cards found, look for any links that might be recipes
            if not recipe_links:
                all_links = soup.find_all('a')
                for link in all_links:
                    href = link.get('href')
                    if href and not href.startswith('#') and not href.startswith('javascript:'):
                        # Look for recipe-like URLs
                        if '/ricette/' in href or href.endswith('.html'):
                            if href.startswith('/'):
                                href = 'https://www.giallozafferano.it' + href
                            recipe_links.append(href)
            
            # Remove duplicates
            recipe_links = list(set(recipe_links))
            
            print(f"Page {page_number}: Found {len(recipe_links)} recipe links")
            for i, recipe_link in enumerate(recipe_links):
                # Add a small delay between requests to be respectful to the website
                if i > 0:
                    import time
                    time.sleep(0.5)  # 500ms delay between requests
                
                # Check if this is an actual recipe link (not a category page)
                if '/ricette/' in recipe_link or recipe_link.endswith('.html'):
                    total_recipes_processed += 1
                    if self.save_recipe(recipe_link):
                        total_recipes_saved += 1
                        page_recipes += 1
                else:
                    # Skip category pages
                    if i < 2:
                        print(f"Skipping category page: {recipe_link}")
            print(f"Page {page_number}: {page_recipes} recipes saved")
            
            # Add a delay between pages to be respectful to the website
            if page_number < total_pages - 1:
                import time
                time.sleep(1)  # 1 second delay between pages
        
        print(f"Total recipes processed: {total_recipes_processed}")
        print(f"Total recipes saved: {total_recipes_saved}")
        print("Scraping completed.")

    def count_total_pages(self):
        number_of_pages = 0
        response = requests.get(self.cookbook_url)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup.find_all(attrs={"class": "disabled total-pages"}):
            number_of_pages = int(tag.text)
        return number_of_pages

    def save_recipe(self, link_recipe_to_download):
        soup = download_page(link_recipe_to_download)
        ingredients = find_ingredients(soup)
        title = find_title(soup)
        if debug:
            print(f"Processing: {title} - Found {len(ingredients)} ingredients")
            if len(ingredients) == 0:
                print(f"No ingredients found for: {title}")
        if ingredients:
            category = find_category(soup)
            n_people = find_n_people(soup)

            file_path = self.calculate_file_path(title)
            if os.path.exists(file_path):
                return False

            model_recipe = ModelRecipe()
            model_recipe.title = title
            model_recipe.ingredients = ingredients
            model_recipe.category = category
            model_recipe.url = link_recipe_to_download
            model_recipe.n_people = n_people

            create_file_json(model_recipe.to_dictionary(), file_path)
            return True
        return False

    def calculate_file_path(self, title):
        compact_name = title.replace(" ", "_").lower()
        return self.folder_recipes + "/" + compact_name + ".json"

    def extract_recipes_from_category(self, category_url):
        """Extract individual recipe links from a category page"""
        recipe_links = []
        try:
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
                    if debug:
                        print(f"Found {len(links)} recipe links with selector '{selector}'")
                    for link in links:
                        href = link.get('href')
                        if href and not href.startswith('#'):
                            # Convert relative URL to absolute URL
                            if href.startswith('/'):
                                href = 'https://www.giallozafferano.it' + href
                            recipe_links.append(href)
                    break  # Use the first selector that finds links
            
            if debug:
                print(f"Extracted {len(recipe_links)} recipe links from category")
                
        except Exception as e:
            if debug:
                print(f"Error extracting recipes from category {category_url}: {e}")
        
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
    # Try multiple selectors for ingredients in the new structure
    ingredient_selectors = [
        '.ingredient',  # Common ingredient class
        '.recipe-ingredient',  # Recipe ingredient class
        '.ingredients-list li',  # Ingredients list items
        '.ingredient-item',  # Ingredient item class
        'li[data-ingredient]',  # Data attribute for ingredients
        '.gz-ingredient'  # Keep old selector as fallback
    ]
    
    for selector in ingredient_selectors:
        ingredient_tags = soup.select(selector)
        if debug:
            print(f"Trying selector '{selector}': Found {len(ingredient_tags)} ingredient tags")
        
        if ingredient_tags:
            for tag in ingredient_tags:
                try:
                    # Try different ways to extract ingredient name and quantity
                    ingredient_text = tag.get_text().strip()
                    if ingredient_text:
                        # Simple parsing: assume format is "ingredient quantity unit"
                        parts = ingredient_text.split()
                        if len(parts) >= 2:
                            # Try to extract quantity and unit from the last parts
                            quantity, udm = get_quantity_udm(ingredient_text)
                            # Assume the ingredient name is everything except quantity/unit
                            name_ingredient = ingredient_text.lower()
                            all_ingredients.append([name_ingredient, quantity, udm])
                except Exception as e:
                    if debug:
                        print(f"Error processing ingredient tag: {e}")
            break  # Use the first selector that finds ingredients
    
    return all_ingredients

def find_n_people(soup):
    for tag in soup.find_all(attrs={"class":"gz-name-featured-data"}):
        match = re.search(r'(\d)\s+persone',tag.text)
        if match:
            n_people = match.group(1)
            return n_people


def find_category(soup):
    # Try multiple selectors for category in the new structure
    category_selectors = [
        '.breadcrumb a',  # Breadcrumb navigation
        '.category',  # Category class
        '.recipe-category',  # Recipe category class
        '.breadcrumb li a',  # Breadcrumb list items
        '.gz-breadcrumb'  # Keep old selector as fallback
    ]
    
    for selector in category_selectors:
        category_tags = soup.select(selector)
        for tag in category_tags:
            if tag.text.strip():
                return tag.text.strip()
    
    return ""



def create_file_json(data, path):
    with open(path, "w") as file:
        file.write(json.dumps(data, ensure_ascii=False))


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
                if debug:
                    print(f"Attempt {attempt + 1} failed for {link_to_download}: {e}")
                    print(f"Retrying in {retry_delay} seconds...")
                import time
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                if debug:
                    print(f"Failed to download {link_to_download} after {max_retries} attempts: {e}")
                raise



