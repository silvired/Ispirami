#!/usr/bin/env python3
"""
Database Query Utility for Ispirami Recipe Recommendation System

This script provides common queries to explore and test the database.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from database_config import get_db_config
import sys

class DatabaseQueries:
    def __init__(self, environment='default'):
        self.config = get_db_config(environment)
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.config)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("✅ Connected to database successfully")
        except psycopg2.Error as e:
            print(f"❌ Error connecting to database: {e}")
            sys.exit(1)
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("✅ Database connection closed")
    
    def get_all_recipes(self):
        """Get all recipes in the database"""
        try:
            self.cursor.execute("""
                SELECT r.title, r.category, r.url, r.n_people
                FROM recipes r
                ORDER BY r.title
            """)
            
            recipes = self.cursor.fetchall()
            print(f"\n📖 All Recipes ({len(recipes)} found):")
            for recipe in recipes:
                print(f"  📖 {recipe['title']}")
                print(f"     Category: {recipe['category']}")
                print(f"     Serves: {recipe['n_people']}")
                print(f"     URL: {recipe['url']}")
                print()
            
            return recipes
        except psycopg2.Error as e:
            print(f"❌ Error querying recipes: {e}")
            return []
    
    def get_recipe_ingredients(self, recipe_title=None, recipe_id=None):
        """Get ingredients for a specific recipe"""
        try:
            if recipe_id:
                self.cursor.execute("""
                    SELECT r.title, i.name, ri.quantity, ri.unit
                    FROM recipes r
                    JOIN recipe_ingredients ri ON r.id = ri.recipe_id
                    JOIN ingredients i ON ri.ingredient_id = i.id
                    WHERE r.id = %s
                    ORDER BY i.name
                """, (recipe_id,))
            elif recipe_title:
                self.cursor.execute("""
                    SELECT r.title, i.name, ri.quantity, ri.unit
                    FROM recipes r
                    JOIN recipe_ingredients ri ON r.id = ri.recipe_id
                    JOIN ingredients i ON ri.ingredient_id = i.id
                    WHERE LOWER(r.title) LIKE LOWER(%s)
                    ORDER BY i.name
                """, (f'%{recipe_title}%',))
            else:
                print("❌ Please provide either recipe_title or recipe_id")
                return []
            
            ingredients = self.cursor.fetchall()
            if ingredients:
                recipe_title = ingredients[0]['title']
                print(f"\n🥕 Ingredients for '{recipe_title}':")
                for ingredient in ingredients:
                    quantity = f"{ingredient['quantity']} {ingredient['unit']}" if ingredient['quantity'] and ingredient['unit'] else "q.b."
                    print(f"  {ingredient['name']}: {quantity}")
            else:
                print("❌ Recipe not found")
            
            return ingredients
        except psycopg2.Error as e:
            print(f"❌ Error querying recipe ingredients: {e}")
            return []
    
    def get_all_ingredients(self):
        """Get all ingredients in the database"""
        try:
            self.cursor.execute("""
                SELECT name, quantity, unit
                FROM ingredients
                ORDER BY name
            """)
            
            ingredients = self.cursor.fetchall()
            print(f"\n🥕 All Ingredients ({len(ingredients)} found):")
            for ingredient in ingredients:
                quantity = f"{ingredient['quantity']} {ingredient['unit']}" if ingredient['quantity'] and ingredient['unit'] else "q.b."
                print(f"  🥕 {ingredient['name']}: {quantity}")
            
            return ingredients
        except psycopg2.Error as e:
            print(f"❌ Error querying ingredients: {e}")
            return []
    
    def search_recipes_by_ingredient(self, ingredient_name):
        """Search recipes that contain a specific ingredient"""
        try:
            self.cursor.execute("""
                SELECT DISTINCT r.title, r.category, r.url
                FROM recipes r
                JOIN recipe_ingredients ri ON r.id = ri.recipe_id
                JOIN ingredients i ON ri.ingredient_id = i.id
                WHERE LOWER(i.name) LIKE LOWER(%s)
                ORDER BY r.title
            """, (f'%{ingredient_name}%',))
            
            recipes = self.cursor.fetchall()
            print(f"\n🔍 Recipes containing '{ingredient_name}' ({len(recipes)} found):")
            for recipe in recipes:
                print(f"  📖 {recipe['title']}")
                print(f"     Category: {recipe['category']}")
                print(f"     URL: {recipe['url']}")
                print()
            
            return recipes
        except psycopg2.Error as e:
            print(f"❌ Error searching recipes: {e}")
            return []
    
    def get_recipe_statistics(self):
        """Get comprehensive recipe statistics"""
        try:
            # Total recipes
            self.cursor.execute("SELECT COUNT(*) as count FROM recipes")
            total_recipes = self.cursor.fetchone()['count']
            
            # Total ingredients
            self.cursor.execute("SELECT COUNT(*) as count FROM ingredients")
            total_ingredients = self.cursor.fetchone()['count']
            
            # Unique ingredients used in recipes
            self.cursor.execute("SELECT COUNT(DISTINCT ingredient_id) as count FROM recipe_ingredients")
            unique_ingredients = self.cursor.fetchone()['count']
            
            # Recipes by category
            self.cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM recipes
                WHERE category IS NOT NULL AND category != ''
                GROUP BY category
                ORDER BY count DESC
                LIMIT 10
            """)
            categories = self.cursor.fetchall()
            
            print("\n📊 Database Statistics:")
            print(f"  🍳 Total recipes: {total_recipes}")
            print(f"  🥕 Total ingredients: {total_ingredients}")
            print(f"  🔗 Unique ingredients used in recipes: {unique_ingredients}")
            
            print(f"\n📂 Top Recipe Categories:")
            for category in categories:
                print(f"  {category['category']}: {category['count']} recipes")
            
            return {
                'total_recipes': total_recipes,
                'total_ingredients': total_ingredients,
                'unique_ingredients': unique_ingredients,
                'categories': categories
            }
        except psycopg2.Error as e:
            print(f"❌ Error getting statistics: {e}")
            return {}
    


def main():
    """Main function with example queries"""
    queries = DatabaseQueries()
    
    try:
        queries.connect()
        
        # Show statistics
        queries.get_recipe_statistics()
        
        # Show all ingredients
        queries.get_all_ingredients()
        
        # Show all recipes
        queries.get_all_recipes()
        
        # Example: Search for recipes with pasta
        queries.search_recipes_by_ingredient("pasta")
        
        # Example: Get ingredients for a specific recipe
        queries.get_recipe_ingredients(recipe_title="carbonara")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        queries.disconnect()

if __name__ == "__main__":
    main() 