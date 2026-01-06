"""
KYRON Blockchain Service
Provides data integrity, immutability, and transparency using blockchain technology
"""

import hashlib
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Block:
    """Represents a single block in the blockchain"""
    
    def __init__(self, index: int, data: Dict, previous_hash: str, timestamp: Optional[str] = None):
        self.index = index
        self.timestamp = timestamp or datetime.now().isoformat()
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
        self.nonce = 0
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the block"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 2):
        """Mine the block (proof of work)"""
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        logger.debug(f"Block mined: {self.hash}")
    
    def to_dict(self) -> Dict:
        """Convert block to dictionary"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce
        }


class Blockchain:
    """Simple blockchain implementation for KYRON data integrity"""
    
    def __init__(self, difficulty: int = 2):
        self.chain: List[Block] = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.pending_transactions: List[Dict] = []
    
    def create_genesis_block(self) -> Block:
        """Create the first block (genesis block)"""
        return Block(0, {
            "type": "genesis",
            "message": "KYRON Blockchain Initialized",
            "timestamp": datetime.now().isoformat()
        }, "0")
    
    def get_latest_block(self) -> Block:
        """Get the most recent block"""
        return self.chain[-1]
    
    def add_block(self, data: Dict) -> Block:
        """Add a new block to the chain"""
        new_block = Block(
            len(self.chain),
            data,
            self.get_latest_block().hash
        )
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        return new_block
    
    def is_valid(self) -> bool:
        """Verify the integrity of the blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if current block hash is valid
            if current_block.hash != current_block.calculate_hash():
                logger.error(f"Invalid hash at block {i}")
                return False
            
            # Check if current block points to previous block
            if current_block.previous_hash != previous_block.hash:
                logger.error(f"Invalid previous hash at block {i}")
                return False
        
        return True
    
    def get_block_by_hash(self, hash: str) -> Optional[Block]:
        """Find block by hash"""
        for block in self.chain:
            if block.hash == hash:
                return block
        return None
    
    def get_chain_data(self) -> List[Dict]:
        """Get all blocks as dictionaries"""
        return [block.to_dict() for block in self.chain]
    
    def verify_data_integrity(self, data_hash: str, block_index: int) -> bool:
        """Verify that data exists in blockchain"""
        if block_index >= len(self.chain):
            return False
        
        block = self.chain[block_index]
        block_data_hash = hashlib.sha256(json.dumps(block.data, sort_keys=True).encode()).hexdigest()
        return block_data_hash == data_hash


class BlockchainService:
    """Service layer for blockchain operations"""
    
    def __init__(self):
        self.blockchain = Blockchain(difficulty=2)
        logger.info("Blockchain service initialized")
    
    def record_automation(self, user_id: str, session_id: str, action: str, data: Dict) -> Dict:
        """
        Record an automation action in the blockchain
        
        Args:
            user_id: User identifier
            session_id: Automation session ID
            action: Action type (e.g., "form_filled", "document_uploaded")
            data: Action data
            
        Returns:
            Block information
        """
        block_data = {
            "type": "automation",
            "user_id": user_id,
            "session_id": session_id,
            "action": action,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        block = self.blockchain.add_block(block_data)
        
        return {
            "success": True,
            "block_index": block.index,
            "block_hash": block.hash,
            "timestamp": block.timestamp
        }
    
    def record_document(self, user_id: str, document_id: str, document_hash: str) -> Dict:
        """
        Record document upload in blockchain
        
        Args:
            user_id: User identifier
            document_id: Document ID
            document_hash: SHA-256 hash of document content
            
        Returns:
            Block information
        """
        block_data = {
            "type": "document",
            "user_id": user_id,
            "document_id": document_id,
            "document_hash": document_hash,
            "timestamp": datetime.now().isoformat()
        }
        
        block = self.blockchain.add_block(block_data)
        
        return {
            "success": True,
            "block_index": block.index,
            "block_hash": block.hash,
            "timestamp": block.timestamp
        }
    
    def verify_integrity(self, block_index: int, expected_hash: str) -> Dict:
        """
        Verify data integrity
        
        Args:
            block_index: Block index to verify
            expected_hash: Expected data hash
            
        Returns:
            Verification result
        """
        if not self.blockchain.is_valid():
            return {
                "success": False,
                "error": "Blockchain integrity check failed"
            }
        
        is_valid = self.blockchain.verify_data_integrity(expected_hash, block_index)
        
        return {
            "success": True,
            "valid": is_valid,
            "block_index": block_index
        }
    
    def get_chain_info(self) -> Dict:
        """Get blockchain information"""
        return {
            "chain_length": len(self.blockchain.chain),
            "is_valid": self.blockchain.is_valid(),
            "latest_block_hash": self.blockchain.get_latest_block().hash,
            "difficulty": self.blockchain.difficulty
        }
    
    def get_user_history(self, user_id: str) -> List[Dict]:
        """Get all blockchain records for a user"""
        user_blocks = []
        for block in self.blockchain.chain:
            if block.data.get("user_id") == user_id:
                user_blocks.append(block.to_dict())
        return user_blocks


# Global instance
_blockchain_service: Optional[BlockchainService] = None

def get_blockchain_service() -> BlockchainService:
    """Get or create global blockchain service instance"""
    global _blockchain_service
    if _blockchain_service is None:
        _blockchain_service = BlockchainService()
    return _blockchain_service

