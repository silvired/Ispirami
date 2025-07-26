class ModelRecipe:
    title = ""
    category = ""
    url = ""
    ingredients = []

    def to_dictionary(self):
        recipe = {
            "title": self.title,
            "category": self.category,
            "ingredients": self.ingredients,
            "url": self.url
        }
        return recipe
