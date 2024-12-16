import os
import secrets

class Config:
    SECRET_KEY = secrets.token_hex(16)
    
    # Configure MariaDB connection
    MYSQL_HOST = os.getenv('DB_HOST')
    MYSQL_USER = os.getenv('DB_USERNAME')
    MYSQL_PASSWORD = os.getenv('DB_PASSWORD')
    MYSQL_DB = os.getenv('DB_DATABASE')
    
class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production-specific configuration."""
    DEBUG = False


class TestingConfig(Config):
    """Testing-specific configuration."""
    TESTING = True
    # Configure MariaDB connection
    MYSQL_HOST = '127.0.0.1'
    MYSQL_USER = 'test' #os.getenv('DB_USERNAME')
    MYSQL_PASSWORD = 'password' #os.getenv('DB_PASSWORD')
    MYSQL_DB = 'mangaweb' #os.getenv('DB_DATABASE')