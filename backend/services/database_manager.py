"""
KYRON Database Manager
Unified interface for MongoDB and PostgreSQL
Automatically chooses the right database for each operation
"""

from typing import Optional, Dict, List, Any
import logging

# Make MongoDB import optional
try:
    from services.database_mongodb import get_mongodb_service
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("MongoDB service not available (pymongo not installed)")
    def get_mongodb_service():
        return None

# Make PostgreSQL import optional
try:
    from services.database_postgres import get_postgres_service
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("PostgreSQL service not available")
    def get_postgres_service():
        return None

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Unified database manager for KYRON"""
    
    def __init__(self):
        """Initialize database manager"""
        self.mongodb = None
        self.postgres = None
        
        # Try to initialize MongoDB (primary)
        try:
            self.mongodb = get_mongodb_service()
            logger.info("MongoDB initialized")
        except Exception as e:
            logger.warning(f"MongoDB not available: {e}")
        
        # Try to initialize PostgreSQL (optional)
        try:
            self.postgres = get_postgres_service()
            if self.postgres:
                logger.info("PostgreSQL initialized")
        except Exception as e:
            logger.info(f"PostgreSQL not available: {e}")
    
    def is_available(self) -> bool:
        """Check if at least one database is available"""
        return self.mongodb is not None or self.postgres is not None
    
    # ==================== User Operations ====================
    
    def create_user(self, user_data: Dict) -> str:
        """Create user - uses MongoDB for flexible schema"""
        if self.mongodb:
            return self.mongodb.create_user(user_data)
        elif self.postgres:
            user_id = self.postgres.create_user(user_data)
            return str(user_id)
        raise Exception("No database available")
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        if self.mongodb:
            return self.mongodb.get_user_by_email(email)
        elif self.postgres:
            return self.postgres.get_user_by_email(email)
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        if self.mongodb:
            return self.mongodb.get_user_by_id(user_id)
        elif self.postgres:
            try:
                uid = int(user_id)
                return self.postgres.get_user_by_id(uid)
            except:
                return None
        return None
    
    # ==================== Profile Operations ====================
    
    def create_or_update_profile(self, user_id: str, profile_data: Dict) -> Dict:
        """Create or update profile - uses MongoDB for flexibility"""
        if self.mongodb:
            return self.mongodb.create_or_update_profile(user_id, profile_data)
        elif self.postgres:
            try:
                uid = int(user_id)
                return self.postgres.create_or_update_profile(uid, profile_data)
            except:
                raise Exception("Invalid user_id format")
        raise Exception("No database available")
    
    def get_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile"""
        if self.mongodb:
            return self.mongodb.get_profile(user_id)
        elif self.postgres:
            try:
                uid = int(user_id)
                return self.postgres.get_profile(uid)
            except:
                return None
        return None
    
    # ==================== Document Operations ====================
    
    def create_document(self, user_id: str, document_data: Dict) -> str:
        """Create document - MongoDB for file metadata"""
        if self.mongodb:
            return self.mongodb.create_document(user_id, document_data)
        raise Exception("MongoDB required for document storage")
    
    def get_user_documents(self, user_id: str) -> List[Dict]:
        """Get user documents"""
        if self.mongodb:
            return self.mongodb.get_user_documents(user_id)
        return []
    
    # ==================== Service Request Operations ====================
    
    def create_service_request(self, user_id: str, request_data: Dict) -> str:
        """Create service request - can use either database"""
        if self.mongodb:
            return self.mongodb.create_service_request(user_id, request_data)
        elif self.postgres:
            try:
                uid = int(user_id)
                req_id = self.postgres.create_service_request(uid, request_data)
                return str(req_id)
            except:
                raise Exception("Invalid user_id format")
        raise Exception("No database available")
    
    def get_user_service_requests(self, user_id: str) -> List[Dict]:
        """Get user service requests"""
        if self.mongodb:
            return self.mongodb.get_user_service_requests(user_id)
        elif self.postgres:
            try:
                uid = int(user_id)
                return self.postgres.get_user_service_requests(uid)
            except:
                return []
        return []
    
    # ==================== Health Check ====================
    
    def health_check(self) -> Dict:
        """Check database health"""
        health = {
            "mongodb": None,
            "postgres": None,
            "status": "unhealthy"
        }
        
        if self.mongodb:
            health["mongodb"] = self.mongodb.health_check()
        
        if self.postgres:
            health["postgres"] = self.postgres.health_check()
        
        if health["mongodb"] or health["postgres"]:
            health["status"] = "healthy"
        
        return health


# Global instance
_db_manager: Optional[DatabaseManager] = None

def get_database_manager() -> DatabaseManager:
    """Get or create global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

