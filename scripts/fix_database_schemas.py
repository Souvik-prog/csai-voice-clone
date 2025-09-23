import sys
import os
from sqlalchemy import create_engine, text

# This is a bit of a trick to make sure the script can find the 'config' module
# It adds the parent directory (the project root) to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings

def reset_database():
    """
    Connects to the PostgreSQL database and drops the specified tables.
    """
    if not settings.DATABASE_URL:
        print("ERROR: DATABASE_URL not found in .env file. Aborting.")
        return

    print("--- DATABASE RESET SCRIPT ---")
    print(f"Connecting to database: {settings.DATABASE_URL.split('@')[-1]}")
    print("\nThis script will execute the following command:")
    print("  DROP TABLE generated_speech, cloned_voices;")
    print("\n\033[91mWARNING: This will permanently delete all data in these tables.\033[0m")
    
    confirm = input("Are you sure you want to continue? (y/n): ")

    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return

    try:
        # Create a SQLAlchemy engine
        engine = create_engine(settings.DATABASE_URL)
        
        # SQL command to be executed
        sql_command = text("DROP TABLE IF EXISTS generated_speech, cloned_voices;")

        with engine.connect() as connection:
            with connection.begin() as transaction:
                print("\nExecuting command...")
                connection.execute(sql_command)
                transaction.commit()
        
        print("\033[92mSuccessfully dropped 'generated_speech' and 'cloned_voices' tables.\033[0m")
        print("They will be recreated the next time you run the FastAPI application.")

    except Exception as e:
        print(f"\033[91mAn error occurred: {e}\033[0m")

if __name__ == "__main__":
    reset_database()
