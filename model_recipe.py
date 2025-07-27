class ModelRecipe:
    title = ""
    category = ""
    url = ""
    ingredients = []
    n_people = ""

    def to_dictionary(self):
        recipe = {
            "title": self.title,
            "category": self.category,
            "ingredients": self.ingredients,
            "url": self.url,
            "n_people": self.n_people
        }
        return recipe
