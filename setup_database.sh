#!/bin/bash

# Database Setup Script for Ispirami Recipe Recommendation System
echo "🚀 Setting up PostgreSQL database for Ispirami..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed or not in PATH"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed or not in PATH"
    exit 1
fi

# Check if PostgreSQL is running
echo "🔍 Checking PostgreSQL connection..."
if ! python3 -c "
import psycopg2
from database_config import get_db_config
try:
    conn = psycopg2.connect(**get_db_config())
    conn.close()
    print('✅ PostgreSQL connection successful')
except Exception as e:
    print(f'❌ PostgreSQL connection failed: {e}')
    exit(1)
" 2>/dev/null; then
    echo "❌ Error: Cannot connect to PostgreSQL"
    echo "Please make sure:"
    echo "  1. PostgreSQL is installed and running"
    echo "  2. Database 'ispirami' exists"
    echo "  3. User credentials in database_config.py are correct"
    exit 1
fi

# Install requirements
echo "📦 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install requirements"
        exit 1
    fi
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

# Check if Recipes directory exists
if [ ! -d "Recipes" ]; then
    echo "⚠️  Recipes directory not found"
    echo "Please run the scraper first to download recipes:"
    echo "  python3 main.py"
    exit 1
fi

# Run database setup
echo "🗄️  Running database setup..."
python3 database_setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Database setup completed successfully!"
    echo ""
    echo "You can now:"
    echo "  • Query the database: python3 database_queries.py"
    echo "  • Update your application to use the database instead of JSON files"
    echo ""
    echo "Database tables created:"
    echo "  • recipes - Recipe information"
    echo "  • ingredients - Ingredient information"
    echo "  • recipe_ingredients - Recipe-ingredient relationships"
    echo "  • available_recipes (view) - Recipes you can make"
    echo ""
else
    echo "❌ Database setup failed"
    exit 1
fi 