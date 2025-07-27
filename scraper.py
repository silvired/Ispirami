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
        for page_number in tqdm(range(1, total_pages), desc="pages…", ascii=False, ncols=75):
            link_list = self.cookbook_url + '/page/' + str(page_number)
            response = requests.get(link_list)
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup.find_all(attrs={"class": "gz-title"}):
                link = tag.a.get("href")
                self.save_recipe(link)

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
        if ingredients:
            title = find_title(soup)
            category = find_category(soup)
            n_people = find_n_people(soup)

            file_path = self.calculate_file_path(title)
            if os.path.exists(file_path):
                return

            model_recipe = ModelRecipe()
            model_recipe.title = title
            model_recipe.ingredients = ingredients
            model_recipe.category = category
            model_recipe.url = link_recipe_to_download
            model_recipe.n_people = n_people

            create_file_json(model_recipe.to_dictionary(), file_path)

    def calculate_file_path(self, title):
        compact_name = title.replace(" ", "_").lower()
        return self.folder_recipes + "/" + compact_name + ".json"

def find_title(soup):
    title_recipe = ""
    for title in soup.find_all(attrs={"class": "gz-title-recipe gz-mBottom2x"}):
        title_recipe = title.text
    return title_recipe


def find_ingredients(soup):
    all_ingredients = []
    for tag in soup.find_all(attrs={"class": "gz-ingredient"}):
        name_ingredient = tag.a.string.lower()
        contents = tag.span.contents[0]
        raw_quantity = re.sub(r"\s+", " ", contents).strip()
        quantity, udm = get_quantity_udm(raw_quantity)
        all_ingredients.append([name_ingredient, quantity, udm])
    return all_ingredients

def find_n_people(soup):
    for tag in soup.find_all(attrs={"class":"gz-name-featured-data"}):
        match = re.search(r'(\d)\s+persone',tag.text)
        if match:
            n_people = match.group(1)
            return n_people


def find_category(soup):
    for tag in soup.find_all(attrs={"class": "gz-breadcrumb"}):
        category = tag.li.a.string
        return category



def create_file_json(data, path):
    with open(path, "w") as file:
        file.write(json.dumps(data, ensure_ascii=False))


def download_page(link_to_download):
    response = requests.get(link_to_download)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup



