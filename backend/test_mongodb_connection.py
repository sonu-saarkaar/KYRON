"""
Test MongoDB Connection Script
Run this to verify MongoDB is accessible at localhost:27017
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    import logging
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # MongoDB connection settings
    MONGODB_URL = "mongodb://localhost:27017"
    MONGODB_DB_NAME = "kyron_db"
    
    print("=" * 60)
    print("Testing MongoDB Connection")
    print("=" * 60)
    print(f"MongoDB URL: {MONGODB_URL}")
    print(f"Database Name: {MONGODB_DB_NAME}")
    print()
    
    try:
        # Connect to MongoDB
        print("Attempting to connect...")
        client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("[SUCCESS] MongoDB connection successful!")
        print()
        
        # List databases
        print("Available databases:")
        db_list = client.list_database_names()
        for db in db_list:
            print(f"  - {db}")
        print()
        
        # Check if kyron_db exists
        db = client[MONGODB_DB_NAME]
        if MONGODB_DB_NAME in db_list:
            print(f"[SUCCESS] Database '{MONGODB_DB_NAME}' exists")
            
            # List collections
            collections = db.list_collection_names()
            if collections:
                print(f"Collections in '{MONGODB_DB_NAME}':")
                for coll in collections:
                    count = db[coll].count_documents({})
                    print(f"  - {coll}: {count} documents")
            else:
                print(f"[INFO] Database '{MONGODB_DB_NAME}' exists but has no collections")
        else:
            print(f"[INFO] Database '{MONGODB_DB_NAME}' will be created on first use")
        
        print()
        print("=" * 60)
        print("[SUCCESS] MongoDB is ready to use!")
        print("=" * 60)
        
        client.close()
        
    except ConnectionFailure as e:
        print("[ERROR] Connection failed!")
        print(f"Error: {e}")
        print()
        print("Please ensure:")
        print("1. MongoDB is installed and running")
        print("2. MongoDB service is started (run: mongod or start MongoDB service)")
        print("3. MongoDB is listening on localhost:27017")
        sys.exit(1)
        
    except ServerSelectionTimeoutError as e:
        print("[ERROR] Server selection timeout!")
        print(f"Error: {e}")
        print()
        print("MongoDB server is not responding. Please check:")
        print("1. Is MongoDB running?")
        print("2. Is it listening on localhost:27017?")
        print("3. Check firewall settings")
        sys.exit(1)
        
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        sys.exit(1)
        
except ImportError:
    print("[ERROR] pymongo is not installed!")
    print()
    print("Please install pymongo:")
    print("  pip install pymongo")
    sys.exit(1)

