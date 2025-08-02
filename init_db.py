#!/usr/bin/env python3
"""
Database initialization script for Court Data Fetcher
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.database import QueryLog, CaseData

def init_database():
    """Initialize the database and create tables"""
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print(" Database tables created successfully!")
            
            # Check if tables exist
            tables = db.engine.table_names()
            print(f" Available tables: {', '.join(tables)}")
            
            # Create downloads directory if it doesn't exist
            downloads_dir = os.path.join('static', 'downloads')
            os.makedirs(downloads_dir, exist_ok=True)
            print(f" Downloads directory created: {downloads_dir}")
            
            print("\n🎉 Database initialization completed successfully!")
            print("You can now run the application with: python app.py")
            
    except Exception as e:
        print(f" Error initializing database: {str(e)}")
        sys.exit(1)

def reset_database():
    """Reset the database (drop all tables and recreate)"""
    try:
        with app.app_context():
            # Drop all tables
            db.drop_all()
            print("  All tables dropped!")
            
            # Create all tables
            db.create_all()
            print(" Database tables recreated successfully!")
            
    except Exception as e:
        print(f" Error resetting database: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    # Load environment variables
    load_dotenv()
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        print(" Resetting database...")
        reset_database()
    else:
        print(" Initializing database...")
        init_database() 