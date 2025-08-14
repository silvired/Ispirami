#!/usr/bin/env python3
"""
Database Setup Script for Ispirami Recipe Recommendation System

This script creates the PostgreSQL database schema and populates it with:
1. Recipes from the JSON files in the Recipes/ directory
2. Recipe-ingredient relationships

Usage:
    python3 database_setup.py
"""

import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import re
from typing import List, Dict, Any, Optional
import sys
from database_config import get_db_config

# Database configuration
DB_CONFIG = get_db_config()

class DatabaseSetup:
    def __init__(self):
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("✅ Connected to PostgreSQL database successfully")
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
    
    def create_schema(self):
        """Create the database schema"""
        schema_sql = """
        -- Create recipes table
        CREATE TABLE IF NOT EXISTS recipes (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            category TEXT,
            url TEXT UNIQUE NOT NULL,
            n_people VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create ingredients table
        CREATE TABLE IF NOT EXISTS ingredients (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL,
            quantity DECIMAL(10,2),
            unit VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create recipe_ingredients junction table
        CREATE TABLE IF NOT EXISTS recipe_ingredients (
            id SERIAL PRIMARY KEY,
            recipe_id INTEGER REFERENCES recipes(id) ON DELETE CASCADE,
            ingredient_id INTEGER REFERENCES ingredients(id) ON DELETE CASCADE,
            quantity DECIMAL(10,2),
            unit VARCHAR(50),
            notes TEXT,
            UNIQUE(recipe_id, ingredient_id)
        );
        
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_recipes_title ON recipes(title);
        CREATE INDEX IF NOT EXISTS idx_recipes_category ON recipes(category);
        CREATE INDEX IF NOT EXISTS idx_ingredients_name ON ingredients(name);
        CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe_id ON recipe_ingredients(recipe_id);
        CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_ingredient_id ON recipe_ingredients(ingredient_id);
        """
        
        try:
            self.cursor.execute(schema_sql)
            self.conn.commit()
            print("✅ Database schema created successfully")
        except psycopg2.Error as e:
            print(f"❌ Error creating schema: {e}")
            self.conn.rollback()
            raise
    
    def clean_ingredient_name(self, ingredient_name: str) -> str:
        """Clean and normalize ingredient names"""
        # Remove extra whitespace and newlines
        cleaned = re.sub(r'\s+', ' ', ingredient_name.strip())
        # Remove common prefixes/suffixes
        cleaned = re.sub(r'^di\s+', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'^del\s+', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'^della\s+', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'^dell\s+', '', cleaned, flags=re.IGNORECASE)
        return cleaned.lower()
    
    def parse_ingredient_quantity(self, ingredient_data: List) -> tuple:
        """Parse ingredient quantity and unit from recipe data"""
        if len(ingredient_data) >= 3:
            quantity = ingredient_data[1]
            unit = ingredient_data[2]
            return (quantity, unit)
        elif len(ingredient_data) >= 2:
            quantity = ingredient_data[1]
            unit = None
            return (quantity, unit)
        else:
            return (1, None)
    
    def insert_ingredient(self, name: str, quantity: Optional[float] = None, 
                         unit: Optional[str] = None) -> int:
        """Insert ingredient and return its ID"""
        try:
            self.cursor.execute("""
                INSERT INTO ingredients (name, quantity, unit)
                VALUES (%s, %s, %s)
                ON CONFLICT (name) DO UPDATE SET
                    quantity = EXCLUDED.quantity,
                    unit = EXCLUDED.unit
                RETURNING id
            """, (name, quantity, unit))
            
            result = self.cursor.fetchone()
            return result['id'] if result else None
        except psycopg2.Error as e:
            print(f"❌ Error inserting ingredient {name}: {e}")
            return None
    
    def insert_recipe(self, title: str, category: str, url: str, n_people: str) -> int:
        """Insert recipe and return its ID"""
        try:
            self.cursor.execute("""
                INSERT INTO recipes (title, category, url, n_people)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (url) DO UPDATE SET
                    title = EXCLUDED.title,
                    category = EXCLUDED.category,
                    n_people = EXCLUDED.n_people
                RETURNING id
            """, (title, category, url, n_people))
            
            result = self.cursor.fetchone()
            return result['id'] if result else None
        except psycopg2.Error as e:
            print(f"❌ Error inserting recipe {title}: {e}")
            return None
    
    def link_recipe_ingredient(self, recipe_id: int, ingredient_id: int, 
                              quantity: Optional[float] = None, 
                              unit: Optional[str] = None, notes: Optional[str] = None):
        """Link recipe with ingredient"""
        try:
            self.cursor.execute("""
                INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, notes)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (recipe_id, ingredient_id) DO UPDATE SET
                    quantity = EXCLUDED.quantity,
                    unit = EXCLUDED.unit,
                    notes = EXCLUDED.notes
            """, (recipe_id, ingredient_id, quantity, unit, notes))
        except psycopg2.Error as e:
            print(f"❌ Error linking recipe {recipe_id} with ingredient {ingredient_id}: {e}")
    

    
    def parse_quantity_string(self, quantity_str: str) -> tuple:
        """Parse quantity string like '1 kg' or '10' into (quantity, unit)"""
        if not quantity_str:
            return (None, None)
        
        # Match patterns like "1 kg", "500 g", "1 l", "10"
        match = re.match(r'^(\d+(?:\.\d+)?)\s*([a-zA-Z]+)?$', quantity_str.strip())
        if match:
            quantity = float(match.group(1))
            unit = match.group(2) if match.group(2) else None
            return (quantity, unit)
        
        return (None, None)
    
    def populate_recipes(self):
        """Populate database with recipes from JSON files"""
        recipes_dir = "Recipes"
        if not os.path.exists(recipes_dir):
            print(f"⚠️  Recipes directory '{recipes_dir}' not found")
            return
        
        recipe_files = [f for f in os.listdir(recipes_dir) if f.endswith('.json')]
        print(f"🍳 Loading {len(recipe_files)} recipes from {recipes_dir}/...")
        
        recipes_processed = 0
        ingredients_processed = 0
        
        for recipe_file in recipe_files:
            try:
                with open(os.path.join(recipes_dir, recipe_file), 'r', encoding='utf-8') as f:
                    recipe_data = json.load(f)
                
                # Insert recipe
                recipe_id = self.insert_recipe(
                    title=recipe_data.get('title', ''),
                    category=recipe_data.get('category', ''),
                    url=recipe_data.get('url', ''),
                    n_people=recipe_data.get('n_people', '')
                )
                
                if not recipe_id:
                    print(f"  ❌ Failed to insert recipe: {recipe_data.get('title', 'Unknown')}")
                    continue
                
                # Process ingredients
                ingredients = recipe_data.get('ingredients', [])
                for ingredient_data in ingredients:
                    if isinstance(ingredient_data, list) and len(ingredient_data) > 0:
                        ingredient_name = ingredient_data[0]
                        quantity, unit = self.parse_ingredient_quantity(ingredient_data)
                        
                        # Clean ingredient name
                        cleaned_name = self.clean_ingredient_name(ingredient_name)
                        
                        # Insert ingredient
                        ingredient_id = self.insert_ingredient(
                            name=cleaned_name,
                            quantity=quantity,
                            unit=unit
                        )
                        
                        if ingredient_id:
                            # Link recipe with ingredient
                            self.link_recipe_ingredient(
                                recipe_id=recipe_id,
                                ingredient_id=ingredient_id,
                                quantity=quantity,
                                unit=unit
                            )
                            ingredients_processed += 1
                
                recipes_processed += 1
                if recipes_processed % 10 == 0:
                    print(f"  📊 Processed {recipes_processed} recipes...")
                
            except json.JSONDecodeError as e:
                print(f"  ❌ Error parsing {recipe_file}: {e}")
            except Exception as e:
                print(f"  ❌ Error processing {recipe_file}: {e}")
        
        self.conn.commit()
        print(f"✅ Recipes populated successfully: {recipes_processed} recipes, {ingredients_processed} ingredients")
    
    def create_views(self):
        """Create useful database views"""
        views_sql = """
        -- View for recipe ingredients with details
        CREATE OR REPLACE VIEW recipe_ingredients_view AS
        SELECT 
            r.id as recipe_id,
            r.title as recipe_title,
            i.id as ingredient_id,
            i.name as ingredient_name,
            ri.quantity as required_quantity,
            ri.unit as required_unit,
            ri.notes
        FROM recipes r
        JOIN recipe_ingredients ri ON r.id = ri.recipe_id
        JOIN ingredients i ON ri.ingredient_id = i.id;
        """
        
        try:
            self.cursor.execute(views_sql)
            self.conn.commit()
            print("✅ Database views created successfully")
        except psycopg2.Error as e:
            print(f"❌ Error creating views: {e}")
            self.conn.rollback()
    
    def show_statistics(self):
        """Show database statistics"""
        try:
            # Count recipes
            self.cursor.execute("SELECT COUNT(*) as count FROM recipes")
            recipe_count = self.cursor.fetchone()['count']
            
            # Count ingredients
            self.cursor.execute("SELECT COUNT(*) as count FROM ingredients")
            ingredient_count = self.cursor.fetchone()['count']
            
            # Count unique ingredients used in recipes
            self.cursor.execute("SELECT COUNT(DISTINCT ingredient_id) as count FROM recipe_ingredients")
            unique_ingredients = self.cursor.fetchone()['count']
            
            print("\n📊 Database Statistics:")
            print(f"  🍳 Total recipes: {recipe_count}")
            print(f"  🥕 Total ingredients: {ingredient_count}")
            print(f"  🔗 Unique ingredients used in recipes: {unique_ingredients}")
            
        except psycopg2.Error as e:
            print(f"❌ Error getting statistics: {e}")
    
    def run_setup(self):
        """Run the complete database setup process"""
        print("🚀 Starting database setup for Ispirami...")
        
        try:
            # Connect to database
            self.connect()
            
            # Create schema
            self.create_schema()
            
            # Populate data
            self.populate_recipes()
            
            # Create views
            self.create_views()
            
            # Show statistics
            self.show_statistics()
            
            print("\n🎉 Database setup completed successfully!")
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            if self.conn:
                self.conn.rollback()
        finally:
            self.disconnect()

def main():
    """Main function"""
    setup = DatabaseSetup()
    setup.run_setup()

if __name__ == "__main__":
    main() 