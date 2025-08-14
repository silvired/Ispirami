# Database Setup Guide for Ispirami

This guide explains how to set up and use the PostgreSQL database for the Ispirami recipe recommendation system.

## Prerequisites

1. **PostgreSQL** installed and running
2. **Python 3.7+** with pip
3. **Recipes data** (JSON files in the `Recipes/` directory)

## Quick Setup

### 1. Install PostgreSQL

**macOS (using Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Create Database

```bash
# Connect to PostgreSQL as postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE ispirami;
CREATE USER ispirami_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ispirami TO ispirami_user;
\q
```

### 3. Configure Database Connection

Edit `database_config.py` and update the connection settings:

```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'ispirami',
    'user': 'ispirami_user',  # or 'postgres'
    'password': 'your_password',
    'port': '5432'
}
```

### 4. Run Database Setup

```bash
# Make setup script executable (if not already)
chmod +x setup_database.sh

# Run the automated setup
./setup_database.sh
```

Or run manually:
```bash
# Install dependencies
pip3 install -r requirements.txt

# Run database setup
python3 database_setup.py
```

## Database Schema

The setup creates the following tables:

### `recipes`
- `id` (SERIAL PRIMARY KEY)
- `title` (VARCHAR(255)) - Recipe name
- `category` (TEXT) - Recipe category
- `url` (TEXT UNIQUE) - Recipe URL
- `n_people` (VARCHAR(50)) - Number of servings
- `created_at` (TIMESTAMP) - Creation timestamp

### `ingredients`
- `id` (SERIAL PRIMARY KEY)
- `name` (VARCHAR(255) UNIQUE) - Ingredient name
- `quantity` (DECIMAL(10,2)) - Quantity
- `unit` (VARCHAR(50)) - Unit of measurement
- `created_at` (TIMESTAMP) - Creation timestamp

### `recipe_ingredients`
- `id` (SERIAL PRIMARY KEY)
- `recipe_id` (INTEGER) - Reference to recipes table
- `ingredient_id` (INTEGER) - Reference to ingredients table
- `quantity` (DECIMAL(10,2)) - Required quantity
- `unit` (VARCHAR(50)) - Required unit
- `notes` (TEXT) - Additional notes

### Views

#### `recipe_ingredients_view`
Detailed view showing recipe-ingredient relationships.

## Usage Examples

### Query Available Recipes

```python
from database_queries import DatabaseQueries

queries = DatabaseQueries()
queries.connect()

# Get all recipes
all_recipes = queries.get_all_recipes()

# Get ingredients for a specific recipe
ingredients = queries.get_recipe_ingredients(recipe_title="carbonara")

# Search recipes by ingredient
pasta_recipes = queries.search_recipes_by_ingredient("pasta")

queries.disconnect()
```

### Direct SQL Queries

```sql
-- Get all recipes
SELECT * FROM recipes;

-- Find recipes with specific ingredients
SELECT r.title, i.name
FROM recipes r
JOIN recipe_ingredients ri ON r.id = ri.recipe_id
JOIN ingredients i ON ri.ingredient_id = i.id
WHERE i.name = 'guanciale';

-- Get recipe statistics by category
SELECT category, COUNT(*) as recipe_count
FROM recipes
GROUP BY category
ORDER BY recipe_count DESC;
```

## Adding Ingredients

To add new ingredients to the database:

```python
import psycopg2
from database_config import get_db_config

conn = psycopg2.connect(**get_db_config())
cursor = conn.cursor()

# Add new ingredient
cursor.execute("""
    INSERT INTO ingredients (name, quantity, unit)
    VALUES (%s, %s, %s)
    ON CONFLICT (name) DO UPDATE SET
        quantity = EXCLUDED.quantity,
        unit = EXCLUDED.unit
""", ('tomatoes', 1.0, 'kg'))

conn.commit()
conn.close()
```

## Testing the Database

Run the query utility to test your database:

```bash
python3 database_queries.py
```

This will show:
- Database statistics
- Available ingredients
- Available recipes
- Example queries

## Troubleshooting

### Connection Issues

1. **"Connection refused"**
   - Ensure PostgreSQL is running: `brew services list` (macOS) or `sudo systemctl status postgresql` (Linux)
   - Check if the port 5432 is correct

2. **"Authentication failed"**
   - Verify username and password in `database_config.py`
   - Check PostgreSQL user permissions

3. **"Database does not exist"**
   - Create the database: `createdb ispirami` or use psql

### Data Issues

1. **No recipes found**
   - Ensure the `Recipes/` directory exists with JSON files
   - Run the scraper first: `python3 main.py`

2. **No recipes found**
   - Ensure the `Recipes/` directory exists with JSON files
   - Run the scraper first: `python3 main.py`

### Performance Issues

1. **Slow queries**
   - Indexes are automatically created for better performance
   - Consider adding more specific indexes for your use case

2. **Large dataset**
   - The database can handle thousands of recipes efficiently
   - Consider using connection pooling for production use

## Migration from JSON to Database

The database setup automatically migrates your existing JSON data:

1. **Recipes**: All JSON files in `Recipes/` directory are imported
2. **Ingredients**: All ingredients from recipes are extracted and stored
3. **Relationships**: Recipe-ingredient relationships are established

After migration, you can:
- Remove the `Recipes/` directory (optional)
- Update your application code to use database queries instead of JSON files
- Use the `DatabaseQueries` class for common operations

## Production Considerations

For production deployment:

1. **Security**
   - Use environment variables for database credentials
   - Implement proper user authentication
   - Use SSL connections

2. **Performance**
   - Use connection pooling
   - Implement caching for frequently accessed data
   - Consider read replicas for high-traffic applications

3. **Backup**
   - Set up regular database backups
   - Test restore procedures

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your PostgreSQL installation
3. Review the database logs
4. Test with the query utility: `python3 database_queries.py` 