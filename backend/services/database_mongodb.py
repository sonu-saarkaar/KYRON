"""
KYRON MongoDB Database Service
Handles all MongoDB operations for user data, profiles, documents, and automation records
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
import logging

# Make pymongo imports optional
try:
    from pymongo import MongoClient, ASCENDING, DESCENDING  # type: ignore
    from pymongo.errors import DuplicateKeyError, OperationFailure  # type: ignore
    from bson import ObjectId  # type: ignore
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    MongoClient = None  # type: ignore
    ASCENDING = None  # type: ignore
    DESCENDING = None  # type: ignore
    DuplicateKeyError = Exception
    OperationFailure = Exception
    ObjectId = None  # type: ignore

try:
    from core.config import settings
except ImportError:
    # Fallback if config not available
    class Settings:
        MONGODB_URL = "mongodb://localhost:27017"
        MONGODB_DB_NAME = "kyron_db"
    settings = Settings()

logger = logging.getLogger(__name__)

class MongoDBService:
    """MongoDB service for KYRON data storage"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        if not PYMONGO_AVAILABLE:
            raise ImportError("pymongo is not installed. Install it with: pip install pymongo")
        
        try:
            self.client = MongoClient(settings.MONGODB_URL)
            self.db = self.client[settings.MONGODB_DB_NAME]
            
            # Collections
            self.users = self.db.users
            self.profiles = self.db.profiles
            self.documents = self.db.documents
            self.automation_sessions = self.db.automation_sessions
            self.service_requests = self.db.service_requests
            self.agent_activity = self.db.agent_activity
            
            # Create indexes
            self._create_indexes()
            
            logger.info(f"MongoDB connected to {settings.MONGODB_URL}/{settings.MONGODB_DB_NAME}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Create database indexes for performance"""
        try:
            # User indexes
            self.users.create_index("email", unique=True)
            self.users.create_index("created_at")
            
            # Profile indexes
            self.profiles.create_index("user_id", unique=True)
            
            # Document indexes
            self.documents.create_index("user_id")
            self.documents.create_index("uploaded_at")
            self.documents.create_index([("user_id", ASCENDING), ("type", ASCENDING)])
            
            # Automation session indexes
            self.automation_sessions.create_index("user_id")
            self.automation_sessions.create_index("created_at")
            self.automation_sessions.create_index([("user_id", ASCENDING), ("status", ASCENDING)])
            
            # Service request indexes
            self.service_requests.create_index("user_id")
            self.service_requests.create_index("status")
            self.service_requests.create_index("created_at")
            
            # Agent activity indexes
            self.agent_activity.create_index("user_id")
            self.agent_activity.create_index("timestamp")
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")
    
    # ==================== User Operations ====================
    
    def create_user(self, user_data: Dict) -> str:
        """Create a new user"""
        user_data["created_at"] = datetime.now()
        user_data["updated_at"] = datetime.now()
        result = self.users.insert_one(user_data)
        return str(result.inserted_id)
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        user = self.users.find_one({"email": email})
        if user:
            user["id"] = str(user["_id"])
            del user["_id"]
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        if not ObjectId:
            return None
        try:
            user = self.users.find_one({"_id": ObjectId(user_id)})
            if user:
                user["id"] = str(user["_id"])
                del user["_id"]
            return user
        except:
            return None
    
    def update_user(self, user_id: str, update_data: Dict) -> bool:
        """Update user data"""
        if not ObjectId:
            return False
        update_data["updated_at"] = datetime.now()
        result = self.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    # ==================== Profile Operations ====================
    
    def create_or_update_profile(self, user_id: str, profile_data: Dict) -> Dict:
        """Create or update user profile"""
        profile_data["user_id"] = user_id
        profile_data["updated_at"] = datetime.now()
        
        existing = self.profiles.find_one({"user_id": user_id})
        
        if existing:
            self.profiles.update_one(
                {"user_id": user_id},
                {"$set": profile_data}
            )
            profile_data["id"] = str(existing["_id"])
        else:
            profile_data["created_at"] = datetime.now()
            result = self.profiles.insert_one(profile_data)
            profile_data["id"] = str(result.inserted_id)
        
        return profile_data
    
    def get_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile"""
        profile = self.profiles.find_one({"user_id": user_id})
        if profile:
            profile["id"] = str(profile["_id"])
            del profile["_id"]
        return profile
    
    # ==================== Document Operations ====================
    
    def create_document(self, user_id: str, document_data: Dict) -> str:
        """Create a new document record"""
        document_data["user_id"] = user_id
        document_data["created_at"] = datetime.now()
        document_data["updated_at"] = datetime.now()
        result = self.documents.insert_one(document_data)
        return str(result.inserted_id)
    
    def get_user_documents(self, user_id: str) -> List[Dict]:
        """Get all documents for a user"""
        documents = list(self.documents.find({"user_id": user_id}).sort("created_at", DESCENDING))
        for doc in documents:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
        return documents
    
    def get_document(self, document_id: str, user_id: str) -> Optional[Dict]:
        """Get a specific document"""
        if not ObjectId:
            return None
        try:
            doc = self.documents.find_one({"_id": ObjectId(document_id), "user_id": user_id})
            if doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
            return doc
        except:
            return None
    
    def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete a document"""
        if not ObjectId:
            return False
        result = self.documents.delete_one({"_id": ObjectId(document_id), "user_id": user_id})
        return result.deleted_count > 0
    
    # ==================== Automation Session Operations ====================
    
    def create_automation_session(self, user_id: str, session_data: Dict) -> str:
        """Create automation session"""
        session_data["user_id"] = user_id
        session_data["created_at"] = datetime.now()
        session_data["status"] = "active"
        result = self.automation_sessions.insert_one(session_data)
        return str(result.inserted_id)
    
    def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get all sessions for a user"""
        sessions = list(self.automation_sessions.find({"user_id": user_id}).sort("created_at", DESCENDING))
        for session in sessions:
            session["id"] = str(session["_id"])
            del session["_id"]
        return sessions
    
    def update_session(self, session_id: str, update_data: Dict) -> bool:
        """Update automation session"""
        if not ObjectId:
            return False
        update_data["updated_at"] = datetime.now()
        result = self.automation_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    # ==================== Service Request Operations ====================
    
    def create_service_request(self, user_id: str, request_data: Dict) -> str:
        """Create a service request"""
        request_data["user_id"] = user_id
        request_data["created_at"] = datetime.now()
        request_data["updated_at"] = datetime.now()
        result = self.service_requests.insert_one(request_data)
        return str(result.inserted_id)
    
    def get_user_service_requests(self, user_id: str) -> List[Dict]:
        """Get all service requests for a user"""
        requests = list(self.service_requests.find({"user_id": user_id}).sort("created_at", DESCENDING))
        for req in requests:
            req["id"] = str(req["_id"])
            del req["_id"]
        return requests
    
    # ==================== Agent Activity Operations ====================
    
    def log_activity(self, user_id: str, activity_data: Dict):
        """Log agent activity"""
        activity_data["user_id"] = user_id
        activity_data["timestamp"] = datetime.now()
        self.agent_activity.insert_one(activity_data)
    
    def get_user_activities(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user activity logs"""
        activities = list(
            self.agent_activity.find({"user_id": user_id})
            .sort("timestamp", DESCENDING)
            .limit(limit)
        )
        for activity in activities:
            activity["id"] = str(activity["_id"])
            del activity["_id"]
        return activities
    
    # ==================== Health Check ====================
    
    def health_check(self) -> Dict:
        """Check database health"""
        try:
            self.client.admin.command('ping')
            return {
                "status": "healthy",
                "database": settings.MONGODB_DB_NAME,
                "collections": {
                    "users": self.users.count_documents({}),
                    "profiles": self.profiles.count_documents({}),
                    "documents": self.documents.count_documents({}),
                    "sessions": self.automation_sessions.count_documents({})
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Global instance
_mongodb_service: Optional[MongoDBService] = None

def get_mongodb_service() -> Optional[MongoDBService]:
    """Get or create global MongoDB service instance"""
    global _mongodb_service
    if not PYMONGO_AVAILABLE:
        logger.warning("pymongo not available. MongoDB features disabled.")
        return None
    
    if _mongodb_service is None:
        try:
            _mongodb_service = MongoDBService()
        except Exception as e:
            logger.warning(f"Failed to initialize MongoDB: {e}")
            return None
    return _mongodb_service

