#!/usr/bin/env python3
"""
Database-based Recipe Matcher for Ispirami

This module provides the same functionality as the original matcher.py
but uses PostgreSQL database queries instead of JSON files.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from database_config import get_db_config
from typing import List, Dict, Any

class DatabaseMatcher:
    def __init__(self, environment='default'):
        self.config = get_db_config(environment)
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.config)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        except psycopg2.Error as e:
            print(f"❌ Error connecting to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def get_all_recipes(self) -> List[str]:
        """
        Get all recipes in the database.
        
        Returns:
            List[str]: List of all recipe URLs
        """
        try:
            self.cursor.execute("""
                SELECT url FROM recipes
                ORDER BY title
            """)
            
            results = self.cursor.fetchall()
            return [row['url'] for row in results]
            
        except psycopg2.Error as e:
            print(f"❌ Error getting recipes: {e}")
            return []
    
    def get_all_recipes_detailed(self) -> List[Dict[str, Any]]:
        """
        Get detailed information about all recipes.
        
        Returns:
            List[Dict]: List of recipe dictionaries with full details
        """
        try:
            self.cursor.execute("""
                SELECT id, title, category, url, n_people
                FROM recipes
                ORDER BY title
            """)
            
            return self.cursor.fetchall()
            
        except psycopg2.Error as e:
            print(f"❌ Error getting detailed recipes: {e}")
            return []
    
    def get_recipe_ingredients(self, recipe_id: int) -> List[Dict[str, Any]]:
        """
        Get ingredients for a specific recipe.
        
        Args:
            recipe_id (int): Recipe ID
            
        Returns:
            List[Dict]: List of ingredient dictionaries
        """
        try:
            self.cursor.execute("""
                SELECT i.name, ri.quantity, ri.unit
                FROM recipe_ingredients ri
                JOIN ingredients i ON ri.ingredient_id = i.id
                WHERE ri.recipe_id = %s
                ORDER BY i.name
            """, (recipe_id,))
            
            return self.cursor.fetchall()
            
        except psycopg2.Error as e:
            print(f"❌ Error getting recipe ingredients: {e}")
            return []
    
    def search_recipes_by_ingredient(self, ingredient_name: str) -> List[Dict[str, Any]]:
        """
        Search for recipes that contain a specific ingredient.
        
        Args:
            ingredient_name (str): Name of ingredient to search for
            
        Returns:
            List[Dict]: List of recipe dictionaries
        """
        try:
            self.cursor.execute("""
                SELECT DISTINCT r.id, r.title, r.category, r.url, r.n_people
                FROM recipes r
                JOIN recipe_ingredients ri ON r.id = ri.recipe_id
                JOIN ingredients i ON ri.ingredient_id = i.id
                WHERE LOWER(i.name) LIKE LOWER(%s)
                ORDER BY r.title
            """, (f'%{ingredient_name}%',))
            
            return self.cursor.fetchall()
            
        except psycopg2.Error as e:
            print(f"❌ Error searching recipes: {e}")
            return []
    
    def get_recipe_by_url(self, url: str) -> Dict[str, Any]:
        """
        Get recipe details by URL.
        
        Args:
            url (str): Recipe URL
            
        Returns:
            Dict: Recipe dictionary or None if not found
        """
        try:
            self.cursor.execute("""
                SELECT id, title, category, url, n_people
                FROM recipes
                WHERE url = %s
            """, (url,))
            
            result = self.cursor.fetchone()
            if result:
                # Get ingredients for this recipe
                ingredients = self.get_recipe_ingredients(result['id'])
                result['ingredients'] = ingredients
            
            return result
            
        except psycopg2.Error as e:
            print(f"❌ Error getting recipe by URL: {e}")
            return None
    
    def get_all_ingredients(self) -> List[Dict[str, Any]]:
        """
        Get all ingredients in the database.
        
        Returns:
            List[Dict]: List of ingredient dictionaries
        """
        try:
            self.cursor.execute("""
                SELECT name, quantity, unit
                FROM ingredients
                ORDER BY name
            """)
            
            return self.cursor.fetchall()
            
        except psycopg2.Error as e:
            print(f"❌ Error getting ingredients: {e}")
            return []
    

    
    def add_ingredient(self, name: str, quantity: float = None, unit: str = None):
        """
        Add a new ingredient.
        
        Args:
            name (str): Ingredient name
            quantity (float): Quantity
            unit (str): Unit of measurement
        """
        try:
            self.cursor.execute("""
                INSERT INTO ingredients (name, quantity, unit)
                VALUES (%s, %s, %s)
                ON CONFLICT (name) DO UPDATE SET
                    quantity = EXCLUDED.quantity,
                    unit = EXCLUDED.unit
            """, (name.lower(), quantity, unit))
            
            self.conn.commit()
            
        except psycopg2.Error as e:
            print(f"❌ Error adding ingredient: {e}")
            self.conn.rollback()
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get database statistics.
        
        Returns:
            Dict: Statistics dictionary
        """
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
            
            return {
                'total_recipes': total_recipes,
                'total_ingredients': total_ingredients,
                'unique_ingredients': unique_ingredients
            }
            
        except psycopg2.Error as e:
            print(f"❌ Error getting statistics: {e}")
            return {}

def print_recipes(matcher: DatabaseMatcher):
    """
    Print all recipes in a formatted way.
    
    Args:
        matcher (DatabaseMatcher): Database matcher instance
    """
    try:
        matcher.connect()
        
        recipe_urls = matcher.get_all_recipes()
        
        if recipe_urls:
            print(f"Found {len(recipe_urls)} recipes.")
            print("Recipes:")
            for url in recipe_urls:
                print(f"  - {url}")
        else:
            print("No recipes found.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        matcher.disconnect()

def main():
    """Main function for testing"""
    matcher = DatabaseMatcher()
    
    try:
        matcher.connect()
        
        # Get statistics
        stats = matcher.get_statistics()
        print("📊 Database Statistics:")
        print(f"  🍳 Total recipes: {stats.get('total_recipes', 0)}")
        print(f"  🥕 Total ingredients: {stats.get('total_ingredients', 0)}")
        print(f"  🔗 Unique ingredients used in recipes: {stats.get('unique_ingredients', 0)}")
        
        # Get all recipes
        all_recipes = matcher.get_all_recipes()
        print(f"\n📖 All Recipes ({len(all_recipes)} found):")
        for url in all_recipes:
            print(f"  📖 {url}")
        
        # Get all ingredients
        ingredients = matcher.get_all_ingredients()
        print(f"\n🥕 All Ingredients ({len(ingredients)} found):")
        for ingredient in ingredients:
            quantity = f"{ingredient['quantity']} {ingredient['unit']}" if ingredient['quantity'] and ingredient['unit'] else "q.b."
            print(f"  🥕 {ingredient['name']}: {quantity}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        matcher.disconnect()

if __name__ == "__main__":
    main() 