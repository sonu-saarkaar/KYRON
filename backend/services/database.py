"""
Database service for MongoDB operations.
Handles all database interactions for KYRON Admin Panel.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

from core.config import settings

class DatabaseService:
    """MongoDB database service"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        self.client = MongoClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB_NAME]
        
        # Collections
        self.admins = self.db.admins
        self.users = self.db.users
        self.login_logs = self.db.login_logs
        self.agent_logs = self.db.agent_logs
        self.error_logs = self.db.error_logs
        self.system_settings = self.db.system_settings
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for performance"""
        # Admin indexes
        self.admins.create_index("email", unique=True)
        self.admins.create_index("status")
        self.admins.create_index("role")
        
        # User indexes
        self.users.create_index("email", unique=True)
        self.users.create_index("status")
        
        # Log indexes
        self.login_logs.create_index("admin_id")
        self.login_logs.create_index("timestamp")
        self.agent_logs.create_index("timestamp")
        self.error_logs.create_index("timestamp")
        
        # System settings
        self.system_settings.create_index("key", unique=True)
    
    # ==================== Admin Operations ====================
    
    def create_admin(self, admin_data: Dict[str, Any]) -> str:
        """
        Create a new admin.
        
        Args:
            admin_data: Admin document data
            
        Returns:
            Created admin ID
            
        Raises:
            ValueError: If email already exists
        """
        admin_data["created_at"] = datetime.utcnow()
        admin_data["updated_at"] = datetime.utcnow()
        admin_data.setdefault("status", "active")
        
        try:
            result = self.admins.insert_one(admin_data)
            return str(result.inserted_id)
        except DuplicateKeyError:
            raise ValueError("Admin with this email already exists")
    
    def get_admin_by_id(self, admin_id: str) -> Optional[Dict[str, Any]]:
        """Get admin by ID"""
        try:
            admin = self.admins.find_one({"_id": ObjectId(admin_id)})
            if admin:
                admin["id"] = str(admin["_id"])
                del admin["_id"]
            return admin
        except:
            return None
    
    def get_admin_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get admin by email"""
        admin = self.admins.find_one({"email": email})
        if admin:
            admin["id"] = str(admin["_id"])
            del admin["_id"]
        return admin
    
    def get_all_admins(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all admins with pagination"""
        admins = list(self.admins.find().skip(skip).limit(limit).sort("created_at", -1))
        for admin in admins:
            admin["id"] = str(admin["_id"])
            del admin["_id"]
        return admins
    
    def count_admins(self) -> int:
        """Count total admins"""
        return self.admins.count_documents({})
    
    def update_admin(self, admin_id: str, update_data: Dict[str, Any]) -> bool:
        """Update admin"""
        update_data["updated_at"] = datetime.utcnow()
        result = self.admins.update_one(
            {"_id": ObjectId(admin_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def block_admin(self, admin_id: str, blocked: bool = True) -> bool:
        """Block or unblock an admin"""
        status_value = "blocked" if blocked else "active"
        return self.update_admin(admin_id, {"status": status_value})
    
    def delete_admin(self, admin_id: str) -> bool:
        """Delete an admin (soft delete by setting status)"""
        return self.update_admin(admin_id, {"status": "deleted"})
    
    # ==================== User Operations ====================
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all users with pagination"""
        users = list(self.users.find().skip(skip).limit(limit).sort("created_at", -1))
        for user in users:
            user["id"] = str(user["_id"])
            del user["_id"]
        return users
    
    def count_users(self) -> int:
        """Count total users"""
        return self.users.count_documents({})
    
    # ==================== Login Log Operations ====================
    
    def create_login_log(self, log_data: Dict[str, Any]) -> str:
        """Create a login log entry"""
        log_data["timestamp"] = datetime.utcnow()
        result = self.login_logs.insert_one(log_data)
        return str(result.inserted_id)
    
    def get_login_logs(
        self, 
        skip: int = 0, 
        limit: int = 100,
        admin_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get login logs with optional filtering"""
        query = {}
        if admin_id:
            query["admin_id"] = admin_id
        
        logs = list(
            self.login_logs.find(query)
            .skip(skip)
            .limit(limit)
            .sort("timestamp", -1)
        )
        for log in logs:
            log["id"] = str(log["_id"])
            del log["_id"]
        return logs
    
    # ==================== Agent Log Operations ====================
    
    def create_agent_log(self, log_data: Dict[str, Any]) -> str:
        """Create an agent log entry"""
        log_data["timestamp"] = datetime.utcnow()
        result = self.agent_logs.insert_one(log_data)
        return str(result.inserted_id)
    
    def get_agent_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        date_filter: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get agent logs with optional date filtering"""
        query = {}
        if date_filter:
            query["timestamp"] = {"$gte": date_filter}
        
        logs = list(
            self.agent_logs.find(query)
            .skip(skip)
            .limit(limit)
            .sort("timestamp", -1)
        )
        for log in logs:
            log["id"] = str(log["_id"])
            del log["_id"]
        return logs
    
    def count_agent_logs_today(self) -> int:
        """Count agent logs from today"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.agent_logs.count_documents({"timestamp": {"$gte": today}})
    
    # ==================== Error Log Operations ====================
    
    def create_error_log(self, log_data: Dict[str, Any]) -> str:
        """Create an error log entry"""
        log_data["timestamp"] = datetime.utcnow()
        result = self.error_logs.insert_one(log_data)
        return str(result.inserted_id)
    
    def get_error_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        date_filter: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get error logs with optional date filtering"""
        query = {}
        if date_filter:
            query["timestamp"] = {"$gte": date_filter}
        
        logs = list(
            self.error_logs.find(query)
            .skip(skip)
            .limit(limit)
            .sort("timestamp", -1)
        )
        for log in logs:
            log["id"] = str(log["_id"])
            del log["_id"]
        return logs
    
    def count_error_logs_today(self) -> int:
        """Count error logs from today"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.error_logs.count_documents({"timestamp": {"$gte": today}})
    
    # ==================== System Settings Operations ====================
    
    def get_system_setting(self, key: str, default: Any = None) -> Any:
        """Get a system setting value"""
        setting = self.system_settings.find_one({"key": key})
        return setting.get("value", default) if setting else default
    
    def set_system_setting(self, key: str, value: Any) -> bool:
        """Set a system setting value"""
        result = self.system_settings.update_one(
            {"key": key},
            {
                "$set": {
                    "value": value,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        return True
    
    def get_agent_status(self) -> bool:
        """Get KYRON agent status (ON/OFF)"""
        return self.get_system_setting("agent_enabled", False)
    
    def set_agent_status(self, enabled: bool) -> bool:
        """Set KYRON agent status"""
        return self.set_system_setting("agent_enabled", enabled)
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all system settings"""
        settings = list(self.system_settings.find())
        return {s["key"]: s.get("value") for s in settings}

