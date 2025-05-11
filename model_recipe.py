class ModelRecipe:
    title = ""
    category = ""
    url = ""
    ingredients = []

    def toDictionary(self):
        recipe = {
            "title": self.title,
            "category": self.category,
            "ingredients": self.ingredients,
            "url": self.url
        }
        return recipe
