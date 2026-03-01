"""
Simple script to test database connection
"""

import sys
from sqlalchemy import text
from connection import engine

def test_connection():
    """Test if database connection is working"""
    try:
        # Try to connect and execute a simple query
        with engine.connect() as connection:
            _result = connection.execute(text("SELECT 1"))
            connection.commit()
            print("✅ Database connection successful!")
            print(f"Connection string: {engine.url}")
            return True
    except Exception as e:
        print("❌ Database connection failed!")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)