"""
Database Configuration for Ispirami Recipe Recommendation System

This file contains database connection settings and can be easily modified
to match your PostgreSQL setup.
"""

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'ispirami',
    'user': 'postgres',
    'password': 'postgres',  # Change this to your actual password
    'port': '5432'
}

# Alternative configurations for different environments
DB_CONFIG_DEV = {
    'host': 'localhost',
    'database': 'ispirami_dev',
    'user': 'postgres',
    'password': 'postgres',
    'port': '5432'
}

DB_CONFIG_PROD = {
    'host': 'your-production-host',
    'database': 'ispirami_prod',
    'user': 'your_prod_user',
    'password': 'your_prod_password',
    'port': '5432'
}

# Connection pool settings (for production use)
POOL_CONFIG = {
    'minconn': 1,
    'maxconn': 10,
    'host': DB_CONFIG['host'],
    'database': DB_CONFIG['database'],
    'user': DB_CONFIG['user'],
    'password': DB_CONFIG['password'],
    'port': DB_CONFIG['port']
}

def get_db_config(environment='default'):
    """
    Get database configuration for specified environment
    
    Args:
        environment (str): 'default', 'dev', or 'prod'
    
    Returns:
        dict: Database configuration dictionary
    """
    configs = {
        'default': DB_CONFIG,
        'dev': DB_CONFIG_DEV,
        'prod': DB_CONFIG_PROD
    }
    
    return configs.get(environment, DB_CONFIG) 