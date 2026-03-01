from connection import engine
from models import Base

def drop_tables():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped successfully.")

if __name__ == "__main__":
    drop_tables()
