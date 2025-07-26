import json
import os

with open("fridge.json", "r") as f:
    fridge = json.load(f)

class Matcher:
    def __init__(self):
        self.fridge = fridge
        self.recipe_path = "Recipes/"
        self.recipe_file_names = os.listdir(self.recipe_path)
        self.ingredients_available = fridge.keys()

    def get_matching_recipes(self):
        matching_recipes = []
        for recipe_file_name in self.recipe_file_names:
            recipe = self.get_recipe_from_file_name(recipe_file_name)
            ingredients = recipe['ingredients']
            url = recipe['url']
            if self.has_all_ingredients(ingredients):
                matching_recipes.append(url)
        return matching_recipes

    def get_recipe_from_file_name(self, recipe_file_name):
        with open(self.recipe_path+recipe_file_name, "r") as file:
            recipe = json.load(file)
        return recipe

    def has_all_ingredients(self,ingredients):
        n_ingredients = len(ingredients)
        n_matches = 0
        for ingredient in ingredients:
            ingredient_name = ingredient[0]
            if self.has_ingredient(ingredient_name):
                n_matches += 1
        return n_ingredients == n_matches

    def has_ingredient(self,recipe_ingredient):
        recipe_ingredient_lower = recipe_ingredient.lower()
        for ingredient in self.ingredients_available:
            ingredient_lower = ingredient.lower()
            # Check if the fridge ingredient is contained in the recipe ingredient
            # or if the recipe ingredient is contained in the fridge ingredient
            if ingredient_lower in recipe_ingredient_lower or recipe_ingredient_lower in ingredient_lower:
                return True
        return False








