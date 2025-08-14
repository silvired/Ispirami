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

debug = True

class Scraper:
    def __init__(self):
        self.cookbook_url = "https://www.giallozafferano.it/ricette-cat"
        self.folder_recipes = "Recipes"
        # Ensure the Recipes directory exists
        if not os.path.exists(self.folder_recipes):
            os.makedirs(self.folder_recipes)

    def download_cookbook(self):
        # Limit to 7 pages for testing purposes
        total_pages = min(3, self.count_total_pages() + 1)
        total_recipes_processed = 0
        total_recipes_saved = 0
        print(f"TESTING MODE: Scraping only {total_pages} pages")
        
        for page_number in tqdm(range(1, total_pages), desc="pages…", ascii=False, ncols=75):
            print(f"\nProcessing page {page_number}/{total_pages-1}...")
            
            # Cautious strategy: Sleep for 5 minutes every 40 pages to avoid being blocked
            # Removed for testing purposes - was causing slowness
            # if page_number > 1 and page_number % 40 == 0:
            #     print(f"\n⚠️  Cautious pause: Sleeping for 5 minutes after processing {page_number} pages...")
            #     import time
            #     time.sleep(300)  # 5 minutes = 300 seconds
            #     print("Resuming scraping...")
            
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
            
            # Method 1: Look for recipe links in elements with class="gz-title"
            recipe_title_elements = soup.find_all(class_="gz-title")
            if recipe_title_elements:
                if debug:
                    print(f"Found {len(recipe_title_elements)} recipe title elements with class 'gz-title'")
                
                for elem in recipe_title_elements:
                    # Extract recipe link from href attribute
                    href = elem.get('href')
                    if href and not href.startswith('#') and not href.startswith('javascript:'):
                        # Convert relative URL to absolute URL
                        if href.startswith('/'):
                            href = 'https://www.giallozafferano.it' + href
                        
                        # Clean up URL by removing anchor fragments
                        if '#' in href:
                            href = href.split('#')[0]
                        
                        recipe_links.append(href)
                        
                        if debug:
                            recipe_name = elem.get('title', 'No title')
                            print(f"  Found recipe: {recipe_name} -> {href}")
            
            # Method 2: If no gz-title elements found, try other selectors
            if not recipe_links:
                recipe_selectors = [
                    'a[href*="/ricette/"]',  # Links containing /ricette/
                    'a[href*=".html"]',      # Links ending with .html
                    '.recipe-card a',        # Recipe card links
                    '.recipe-item a',        # Recipe item links
                    'h2 a',                  # Links within h2 tags (recipe titles)
                    'h3 a',                  # Links within h3 tags
                ]
                
                for selector in recipe_selectors:
                    try:
                        links = soup.select(selector)
                        if links:
                            if debug:
                                print(f"Found {len(links)} links with selector '{selector}'")
                            for link in links:
                                href = link.get('href')
                                if href and not href.startswith('#') and not href.startswith('javascript:'):
                                    # Convert relative URL to absolute URL
                                    if href.startswith('/'):
                                        href = 'https://www.giallozafferano.it' + href
                                    
                                    # Clean up URL by removing anchor fragments
                                    if '#' in href:
                                        href = href.split('#')[0]
                                    
                                    recipe_links.append(href)
                            break  # Use the first selector that finds links
                    except Exception as e:
                        if debug:
                            print(f"Error with selector '{selector}': {e}")
            
            # Method 3: If still no links, look for any links that might be recipes
            if not recipe_links:
                all_links = soup.find_all('a')
                for link in all_links:
                    href = link.get('href')
                    if href and not href.startswith('#') and not href.startswith('javascript:'):
                        # Look for recipe-like URLs but exclude category pages
                        if '/ricette/' in href and '/ricette-cat/' not in href and href.endswith('.html'):
                            if href.startswith('/'):
                                href = 'https://www.giallozafferano.it' + href
                            
                            # Clean up URL by removing anchor fragments
                            if '#' in href:
                                href = href.split('#')[0]
                            
                            recipe_links.append(href)
            
            # Remove duplicates
            recipe_links = list(set(recipe_links))
            
            print(f"Page {page_number}: Found {len(recipe_links)} recipe links")
            if debug and recipe_links:
                print("Sample recipe links found:")
                for i, link in enumerate(recipe_links[:5]):  # Show first 5 links
                    print(f"  {i+1}: {link}")
            
            for i, recipe_link in enumerate(recipe_links):
                # Process all recipe links found (we know they're correct from gz-title elements)
                total_recipes_processed += 1
                if self.process_recipe(recipe_link):
                    total_recipes_saved += 1
                    page_recipes += 1
                
            print(f"Page {page_number}: {page_recipes} recipes processed")
            
            # No delay between pages for faster testing
        
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

    def process_recipe(self, link_recipe_to_download):
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

            # Process ingredients with NLP instead of saving to file
            print(f"\n=== RECIPE: {title} ===")
            print(f"Category: {category}")
            print(f"People: {n_people}")
            print(f"URL: {link_recipe_to_download}")
            print("\n=== INGREDIENT ANALYSIS ===")
            
            for i, ingredient in enumerate(ingredients, 1):
                # Handle ingredients as [name, quantity] pairs
                if isinstance(ingredient, list) and len(ingredient) == 2:
                    ingredient_name = ingredient[0]
                    ingredient_quantity = ingredient[1]
                else:
                    # Fallback for single string ingredients
                    ingredient_name = ingredient if isinstance(ingredient, str) else str(ingredient)
                    ingredient_quantity = ""
                
                # Clean up ingredient text: remove external spaces, tabs, and newlines
                ingredient_name = ingredient_name.replace('\t', '').replace('\n', '').replace('\r', '') if ingredient_name else ""
                ingredient_quantity = ingredient_quantity.replace('\t', '').replace('\n', '').replace('\r', '') if ingredient_quantity else ""
                
                # Remove multiple consecutive spaces
                ingredient_name = ' '.join(ingredient_name.split()) if ingredient_name else ""
                ingredient_quantity = ' '.join(ingredient_quantity.split()) if ingredient_quantity else ""
                
                # Create full ingredient by combining name and quantity
                if ingredient_name and ingredient_quantity:
                    full_ingredient = f"{ingredient_name} {ingredient_quantity}"
                elif ingredient_name:
                    full_ingredient = ingredient_name
                else:
                    full_ingredient = ingredient_quantity
                
                
                # Use NLP to analyze the full ingredient
                doc = nlp(full_ingredient)
                print(f"  Tokens: {len(doc)}")
                
                for token in doc:
                    print(f"    {token.text:<15} {token.pos_:<10} {token.dep_:<10}")
            
            print("\n" + "="*50)
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
    
    # 1 - get all ingredients tags having class_="gz-ingredient"
    ingredient_tags = soup.find_all(class_="gz-ingredient")
    
    print(f"Found {len(ingredient_tags)} ingredient tags")
    
    # 2 - loop through ingredients and enumerate them
    for i, tag in enumerate(ingredient_tags, 1):
        print(f"Processing ingredient {i}")
        
        # 4 - get ingredient name from tag <a>
        name_elem = tag.find('a')
        ingredient_name = ""
        if name_elem:
            ingredient_name = name_elem.get_text()
        
        # 5 - print ingredient name raw
        print(f"  Ingredient name raw: '{ingredient_name}'")
        
        # 6 - get ingredient quantity from tag <span>
        quantity_elem = tag.find('span')
        ingredient_quantity = ""
        if quantity_elem:
            ingredient_quantity = quantity_elem.get_text()
        
        # 7 - print ingredient quantity raw
        print(f"  Ingredient quantity raw: '{ingredient_quantity}'")
        
        # Store the ingredient data
        all_ingredients.append([ingredient_name, ingredient_quantity])
        print("  ---")
    
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

# Main execution block
if __name__ == "__main__":
    print("Starting the scraper...")
    scraper = Scraper()
    scraper.download_cookbook()



