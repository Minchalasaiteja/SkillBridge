"""
MongoDB Database Configuration and Models
Handles all database operations for SkillBridge
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pymongo import MongoClient
from pymongo.collection import Collection
from bson import ObjectId
import logging
from config import settings

logger = logging.getLogger(__name__)


class MongoDBConnection:
    """MongoDB connection manager"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
    
    def connect(self):
        """Establish MongoDB connection"""
        try:
            self.client = MongoClient(settings.mongodb_uri)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[settings.mongodb_db_name]
            logger.info(f"Connected to MongoDB: {settings.mongodb_db_name}")
            self._create_indexes()
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def _create_indexes(self):
        """Create necessary database indexes"""
        try:
            # Learner profiles index
            self.db.learner_profiles.create_index("learner_id", unique=True)
            self.db.learner_profiles.create_index("created_at")
            
            # Pathways index
            self.db.pathways.create_index("learner_id")
            self.db.pathways.create_index("created_at")
            
            # Sessions index
            self.db.sessions.create_index("session_id", unique=True)
            self.db.sessions.create_index("learner_id")
            self.db.sessions.create_index("expires_at", expireAfterSeconds=3600)
            
            # Agent logs index
            self.db.agent_logs.create_index("agent_name")
            self.db.agent_logs.create_index("timestamp")
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Index creation warning: {str(e)}")
    
    def get_collection(self, collection_name: str) -> Collection:
        """Get collection from database"""
        return self.db[collection_name]


class LearnerProfile:
    """Learner profile operations"""
    
    def __init__(self, db_connection: MongoDBConnection):
        self.collection = db_connection.get_collection("learner_profiles")
    
    def create(self, learner_data: Dict[str, Any]) -> str:
        """Create new learner profile"""
        learner_data["created_at"] = datetime.utcnow()
        learner_data["updated_at"] = datetime.utcnow()
        result = self.collection.insert_one(learner_data)
        logger.info(f"Created learner profile: {result.inserted_id}")
        return str(result.inserted_id)
    
    def find_by_id(self, learner_id: str) -> Optional[Dict]:
        """Find learner by ID"""
        return self.collection.find_one({"learner_id": learner_id})
    
    def find_by_mongo_id(self, mongo_id: str) -> Optional[Dict]:
        """Find learner by MongoDB ID"""
        return self.collection.find_one({"_id": ObjectId(mongo_id)})
    
    def update(self, learner_id: str, update_data: Dict[str, Any]) -> bool:
        """Update learner profile"""
        update_data["updated_at"] = datetime.utcnow()
        result = self.collection.update_one(
            {"learner_id": learner_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def find_all(self, limit: int = 100) -> List[Dict]:
        """Find all learner profiles"""
        return list(self.collection.find().limit(limit))


class Pathway:
    """Learning pathway operations"""
    
    def __init__(self, db_connection: MongoDBConnection):
        self.collection = db_connection.get_collection("pathways")
    
    def create(self, pathway_data: Dict[str, Any]) -> str:
        """Create new pathway"""
        pathway_data["created_at"] = datetime.utcnow()
        pathway_data["updated_at"] = datetime.utcnow()
        result = self.collection.insert_one(pathway_data)
        logger.info(f"Created pathway: {result.inserted_id}")
        return str(result.inserted_id)
    
    def find_by_learner(self, learner_id: str) -> Optional[Dict]:
        """Find pathway by learner ID"""
        return self.collection.find_one(
            {"learner_id": learner_id},
            sort=[("created_at", -1)]
        )
    
    def find_recent(self, limit: int = 10) -> List[Dict]:
        """Find recent pathways"""
        return list(self.collection.find().sort("created_at", -1).limit(limit))
    
    def update(self, pathway_id: str, update_data: Dict[str, Any]) -> bool:
        """Update pathway"""
        update_data["updated_at"] = datetime.utcnow()
        result = self.collection.update_one(
            {"_id": ObjectId(pathway_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0


class Session:
    """Session management operations"""
    
    def __init__(self, db_connection: MongoDBConnection):
        self.collection = db_connection.get_collection("sessions")
    
    def create(self, session_data: Dict[str, Any]) -> str:
        """Create new session"""
        session_data["created_at"] = datetime.utcnow()
        result = self.collection.insert_one(session_data)
        return str(result.inserted_id)
    
    def find_by_id(self, session_id: str) -> Optional[Dict]:
        """Find session by ID"""
        return self.collection.find_one({"session_id": session_id})
    
    def update(self, session_id: str, update_data: Dict[str, Any]) -> bool:
        """Update session"""
        result = self.collection.update_one(
            {"session_id": session_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def delete(self, session_id: str) -> bool:
        """Delete session"""
        result = self.collection.delete_one({"session_id": session_id})
        return result.deleted_count > 0


class AgentLog:
    """Agent execution logging"""
    
    def __init__(self, db_connection: MongoDBConnection):
        self.collection = db_connection.get_collection("agent_logs")
    
    def log_execution(self, log_data: Dict[str, Any]) -> str:
        """Log agent execution"""
        log_data["timestamp"] = datetime.utcnow()
        result = self.collection.insert_one(log_data)
        return str(result.inserted_id)
    
    def find_by_agent(self, agent_name: str, limit: int = 100) -> List[Dict]:
        """Find logs by agent name"""
        return list(
            self.collection.find({"agent_name": agent_name})
            .sort("timestamp", -1)
            .limit(limit)
        )
    
    def find_by_learner(self, learner_id: str, limit: int = 100) -> List[Dict]:
        """Find logs by learner ID"""
        return list(
            self.collection.find({"learner_id": learner_id})
            .sort("timestamp", -1)
            .limit(limit)
        )


class ResourceDAO:
    """Course/resource catalog operations"""

    def __init__(self, db_connection: MongoDBConnection):
        self.collection = db_connection.get_collection("resources")

    def create_many(self, resources: List[Dict[str, Any]]) -> int:
        """Insert many resources, return count inserted"""
        if not resources:
            return 0
        for r in resources:
            r.setdefault("created_at", datetime.utcnow())
        result = self.collection.insert_many(resources)
        return len(result.inserted_ids)

    def find_recent(self, limit: int = 50) -> List[Dict]:
        return list(self.collection.find().sort("created_at", -1).limit(limit))

    def count(self) -> int:
        return self.collection.count_documents({})


# Initialize database connection
db = MongoDBConnection()


def init_db():
    """Initialize database connection (non-blocking; logs warnings if unavailable)"""
    try:
        db.connect()
    except Exception as e:
        logger.warning(f"MongoDB connection unavailable at startup (continuing anyway): {str(e)}")


def close_db():
    """Close database connection"""
    db.disconnect()


def get_db_instance() -> MongoDBConnection:
    """Get database instance"""
    return db
