"""
Script to empty all data from database tables defined in models.py
"""
import sys
from sqlalchemy import text
from connection import engine, SessionLocal
from models import Base

def empty_database():
    """Empty all data from database tables"""
    tables = [
        'digests',
        'youtube_videos', 
        'openai_articles',
        'anthropic_articles',
        'wired_articles'
    ]
    
    try:
        # Use raw SQL for TRUNCATE operations
        with engine.connect() as connection:
            # Start transaction
            with connection.begin():
                # Truncate tables in reverse order to handle foreign key constraints
                for table in tables:
                    print(f"Emptying table: {table}")
                    connection.execute(text(f'TRUNCATE TABLE {table} CASCADE'))
                    print(f"✅ Emptied {table}")
                
                # Commit the transaction
                connection.commit()
            
        print("✅ All tables emptied successfully!")
        return True
        
    except Exception as e:
        print("❌ Failed to empty database!")
        print(f"Error: {e}")
        return False

def get_table_counts():
    """Get current row counts for all tables"""
    tables = [
        'digests',
        'youtube_videos', 
        'openai_articles',
        'anthropic_articles'
    ]
    
    try:
        with engine.connect() as connection:
            for table in tables:
                result = connection.execute(text(f'SELECT COUNT(*) FROM {table}'))
                count = result.scalar()
                print(f"{table}: {count} rows")
                
    except Exception as e:
        print(f"Error getting counts: {e}")

if __name__ == "__main__":
    print("Current table counts:")
    get_table_counts()
    
    print("\nEmptying all tables...")
    success = empty_database()
    
    print("\nTable counts after emptying:")
    get_table_counts()
    
    sys.exit(0 if success else 1)