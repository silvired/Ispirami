import json
import os
import re
import sys
import time
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

sys.path.append(os.path.abspath(".."))

from model_recipe import ModelRecipe

class Scraper:
    def __init__(self, starting_page=1, ending_page=1, resume=False):
        self.cookbook_url = "https://www.giallozafferano.it/ricette-cat"
        self.folder_recipes = "recipes"
        self.starting_page = starting_page
        self.ending_page = ending_page
        
        # Ensure the recipes directory exists
        if not os.path.exists(self.folder_recipes):
            os.makedirs(self.folder_recipes)
        
        # Resume from last processed page if requested
        if resume:
            self.resume_from_last_page()

    def get_last_processed_page(self):
        """
        Get the last processed page number by checking existing recipe files
        """
        if not os.path.exists(self.folder_recipes):
            return 0
            
        # This is a simple heuristic - in practice you might want to store this in a separate file
        # For now, we'll assume the user knows where they left off
        return 0

    def resume_from_last_page(self):
        """
        Resume scraping from the last processed page
        """
        last_page = self.get_last_processed_page()
        if last_page > 0:
            self.starting_page = last_page + 1

    def get_recipes_links(self, page_url):
        """
        Extract recipe links from a page listing recipes
        """
        max_retries = 3
        retry_delay = 60  # 1 minute delay between retries
        
        for attempt in range(max_retries):
            try:
                response = requests.get(page_url, timeout=30)
                response.raise_for_status()
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
                else:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        return []
                        
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    return []
        
        return []

    def count_total_pages(self):
        number_of_pages = 0
        response = requests.get(self.cookbook_url)
        soup = BeautifulSoup(response.text, "html.parser")
        
        pagination_tags = soup.find_all(attrs={"class": "disabled total-pages"})
        
        for tag in pagination_tags:
            number_of_pages = int(tag.text)
        
        return number_of_pages

    def download_cookbook(self):
        # Determine the total number of pages available
        total_available_pages = self.count_total_pages()
        
        # Determine the actual ending page
        if self.ending_page == 'max':
            actual_ending_page = total_available_pages
        else:
            actual_ending_page = min(self.ending_page, total_available_pages)
        
        # Validate starting page
        if self.starting_page < 1:
            self.starting_page = 1
        if self.starting_page > total_available_pages:
            return
        
        total_recipes_processed = 0
        total_recipes_saved = 0
        
        for page_number in range(self.starting_page, actual_ending_page + 1):
            print("-" * 50)
            print(f"Scraping page number {page_number}/{actual_ending_page}")
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
                
                # Add 1 second delay between recipes
                if i < len(recipe_links) - 1:  # Don't delay after the last recipe
                    time.sleep(5)
            
            # Add 10 seconds delay between pages (except after the last page)
            if page_number < actual_ending_page:
                time.sleep(30)
                
        print(f"Total recipes processed: {total_recipes_processed}")
        print(f"Total recipes saved: {total_recipes_saved}")
        print("Scraping completed.")
        

    


    def recipe_exists(self, title):
        """
        Check if a recipe with the given title already exists
        """
        filename = self.calculate_file_path(title)
        return os.path.exists(filename)

    def process_recipe(self, link_recipe_to_download):
        soup = download_page(link_recipe_to_download)
        
        # Check if page download failed
        if soup is None:
            print(f"Failed to download page: {link_recipe_to_download}")
            return False
            
        ingredients = find_ingredients(soup)
        title = find_title(soup)
        print(f"Processing recipe: {title}")
        
        # Check if recipe already exists
        if self.recipe_exists(title):
            return False
            
        if ingredients:
            categories = find_category(soup)
            recipe_features = find_recipe_features(soup)
            recipe_nutritional_values = find_recipe_nutritional_values(soup)

            # Save recipe to JSON file
            recipe_data = {
                'title': title,
                'ingredients': ingredients,
                'features': recipe_features,
                'nutritional_values': recipe_nutritional_values,
                'recipe_link': link_recipe_to_download
            }
            
            # Save recipe to JSON file
            if self.save_recipe_to_json(recipe_data):
                return True
            else:
                print(f"Failed to save recipe: {title}")
                return False
        return False

    def calculate_file_path(self, title):
        """
        Calculate a safe filename for the recipe
        """
        # Remove or replace problematic characters for filenames
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
        # Replace multiple spaces with single underscore
        safe_title = re.sub(r'\s+', '_', safe_title)
        # Remove leading/trailing underscores
        safe_title = safe_title.strip('_')
        # Limit length to avoid filesystem issues
        if len(safe_title) > 100:
            safe_title = safe_title[:100]
        
        return os.path.join(self.folder_recipes, f"{safe_title}.json")
    
    def save_recipe_to_json(self, recipe_data):
        """
        Save recipe data to a JSON file
        
        Args:
            recipe_data (dict): Dictionary containing recipe information
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Calculate filename from title
            filename = self.calculate_file_path(recipe_data['title'])
            
            # Ensure the recipes directory exists
            os.makedirs(self.folder_recipes, exist_ok=True)
            
            # Save recipe to JSON file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(recipe_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving recipe '{recipe_data.get('title', 'Unknown')}': {e}")
            return False

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
    if not ingredient_tags:
        print("Warning: No ingredient tags found on this page")
        return []
        
    for i, tag in enumerate(ingredient_tags, 1):
        try:
            name_elem = tag.find('a')
            if not name_elem:
                continue
                
            ingredient_name = name_elem.get_text().strip()
            if not ingredient_name:
                continue
                
            quantity_elem = tag.find('span')
            if not quantity_elem:
                continue
                
            ingredient_quantity_raw = quantity_elem.get_text()
            ingredient_quantity = " ".join(ingredient_quantity_raw.replace('\t', '').split('\n')).strip()
            
            # Use structured format with colon separator for better NLP analysis
            full_ingredient = f"{ingredient_name}: {ingredient_quantity}"
            all_ingredients.append(full_ingredient)
            
        except Exception as e:
            print(f"Error processing ingredient {i}: {e}")
            continue
    
    return all_ingredients


def find_category(soup):
    try:
        cat_tag = soup.find(class_="gz-breadcrumb")
        if not cat_tag:
            print("Warning: No breadcrumb found on this page")
            return []
            
        categories = cat_tag.get_text().split('\n')
        categories = [cat.strip() for cat in categories if cat.strip()]
        return categories
        
    except Exception as e:
        print(f"Error processing categories: {e}")
        return []


def find_recipe_features(soup):
    recipe_features = {}
    try:
        recipes_data_tags = soup.find_all(class_="gz-name-featured-data")
        if not recipes_data_tags:
            print("Warning: No recipe features found on this page")
            return {}
            
        for tag in recipes_data_tags:
            try:
                text = tag.get_text().strip()
                if ": " in text:
                    # Split on first occurrence of ': ' to handle multiple colons
                    parts = text.split(': ', 1)
                    if len(parts) == 2:
                        feature, value = parts
                        recipe_features[feature.strip()] = value.strip()
            except Exception as e:
                print(f"Error processing recipe feature: {e}")
                continue
                
    except Exception as e:
        print(f"Error processing recipe features: {e}")
        
    return recipe_features


def find_recipe_nutritional_values(soup):
    recipe_nutritional_values = {}
    try:
        macros_tags = soup.find_all(class_="gz-list-macros-name")
        unit_tags = soup.find_all(class_="gz-list-macros-unit")
        value_tags = soup.find_all(class_="gz-list-macros-value")
        
        if not macros_tags or not value_tags:
            print("Warning: No nutritional values found on this page")
            return {}
            
        macros = [tag.get_text().strip() for tag in macros_tags]
        macros_amended = [macro.lstrip() for macro in macros]
        values = []
        
        for tag in value_tags:
            try:
                tag_text = tag.get_text().strip()
                if tag_text[-3:] == ".00":
                    tag_text = tag_text[:-3]
                values.append(float(tag_text.replace(',','.')))
            except (ValueError, AttributeError) as e:
                print(f"Error processing nutritional value: {e}")
                continue

        # Only process if we have matching numbers of macros and values
        if len(macros_amended) == len(values):
            for i in range(len(macros_amended)):
                recipe_nutritional_values[macros_amended[i]] = values[i]
        else:
            print(f"Warning: Mismatch between macros ({len(macros_amended)}) and values ({len(values)})")
            
    except Exception as e:
        print(f"Error processing nutritional values: {e}")
        
    return recipe_nutritional_values


def download_page(link_to_download):
    max_retries = 3
    retry_delay = 30  # 30 seconds delay between retries
    
    for attempt in range(max_retries):
        try:
            response = requests.get(link_to_download, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            return soup
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print("Max retries reached, returning None")
                return None
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print("Max retries reached, returning None")
                return None
    
    return None




# Main execution block
if __name__ == "__main__":
    print("Starting the scraper...")
    
    # Example 1: Scrape from page 77 to max (since page 76 was the last fully scraped)
    scraper = Scraper(starting_page=337, ending_page='max', resume=True)
    scraper.download_cookbook()
    
    # Example 2: Scrape a specific range of pages
    # scraper = Scraper(starting_page=77, ending_page=100)
    # scraper.download_cookbook()
    
    # Example 3: Resume from where you left off (if you implement progress tracking)
    # scraper = Scraper(starting_page=1, ending_page='max', resume=True)
    # scraper.download_cookbook()



