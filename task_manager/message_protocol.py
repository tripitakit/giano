"""
Enhanced Message Protocol for AI Agent Collaboration
====================================================

This module provides a comprehensive messaging system for secure, validated,
and efficient communication between AI agents in collaborative environments.

Features:
- Expanded message types (HEARTBEAT, STATUS_UPDATE, COLLABORATION_REQUEST, etc.)
- Message validation and encryption
- Routing capabilities and priority handling
- Real-time communication with delivery confirmation
- Security layer with authentication

Author: Agent Black (Primary Architect)
Reviewed by: Agent White (Quality Assurance Specialist)
"""

import json
import time
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import fcntl
from cryptography.fernet import Fernet
import base64


class MessageType(Enum):
    """Enumeration of all supported message types"""
    # Basic communication types
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    NOTIFICATION = "NOTIFICATION"
    ERROR = "ERROR"
    
    # Enhanced collaboration types (Agent White's recommendations)
    HEARTBEAT = "HEARTBEAT"
    STATUS_UPDATE = "STATUS_UPDATE"
    COLLABORATION_REQUEST = "COLLABORATION_REQUEST"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    APPROVAL_GRANTED = "APPROVAL_GRANTED"
    TASK_DELEGATION = "TASK_DELEGATION"
    
    # Synchronization types
    LOCK_REQUEST = "LOCK_REQUEST"
    LOCK_GRANTED = "LOCK_GRANTED"
    LOCK_RELEASED = "LOCK_RELEASED"
    DEADLOCK_DETECTED = "DEADLOCK_DETECTED"


class MessagePriority(Enum):
    """Message priority levels for routing"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class MessageStatus(Enum):
    """Message delivery status"""
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    FAILED = "FAILED"


@dataclass
class Message:
    """Enhanced message structure with full metadata"""
    msg_id: str
    msg_type: MessageType
    from_agent: str
    to_agent: str
    content: Dict[str, Any]
    timestamp: str
    priority: MessagePriority = MessagePriority.NORMAL
    status: MessageStatus = MessageStatus.PENDING
    requires_response: bool = False
    correlation_id: Optional[str] = None
    encryption_key: Optional[str] = None
    checksum: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    expiry_time: Optional[str] = None
    
    def __post_init__(self):
        """Generate checksum and handle initialization"""
        if not self.checksum:
            self.checksum = self._generate_checksum()
    
    def _generate_checksum(self) -> str:
        """Generate message integrity checksum"""
        content_str = json.dumps(self.content, sort_keys=True)
        message_data = f"{self.msg_id}{self.msg_type.value}{self.from_agent}{self.to_agent}{content_str}{self.timestamp}"
        return hashlib.sha256(message_data.encode()).hexdigest()
    
    def is_valid(self) -> bool:
        """Validate message integrity"""
        return self.checksum == self._generate_checksum()
    
    def is_expired(self) -> bool:
        """Check if message has expired"""
        if not self.expiry_time:
            return False
        return datetime.now().isoformat() > self.expiry_time


class MessageValidator:
    """Message validation and security layer (Agent White's recommendation)"""
    
    def __init__(self, security_key: Optional[str] = None):
        self.security_key = security_key or self._generate_security_key()
        self.fernet = Fernet(self.security_key.encode()[:44] + b'=')
    
    def _generate_security_key(self) -> str:
        """Generate a security key for encryption"""
        return base64.urlsafe_b64encode(os.urandom(32)).decode()[:43]
    
    def validate_message(self, message: Message) -> tuple[bool, str]:
        """Validate message structure and integrity"""
        try:
            # Check required fields
            if not all([message.msg_id, message.msg_type, message.from_agent, 
                       message.to_agent, message.content, message.timestamp]):
                return False, "Missing required fields"
            
            # Check message integrity
            if not message.is_valid():
                return False, "Message integrity check failed"
            
            # Check expiry
            if message.is_expired():
                return False, "Message has expired"
            
            # Validate agent IDs format
            if not self._validate_agent_id(message.from_agent) or not self._validate_agent_id(message.to_agent):
                return False, "Invalid agent ID format"
            
            return True, "Message is valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _validate_agent_id(self, agent_id: str) -> bool:
        """Validate agent ID format"""
        import re
        pattern = r"^agent[1-9]\d*$|^agent_(black|white)$"
        return bool(re.match(pattern, agent_id.lower()))
    
    def encrypt_content(self, content: Dict[str, Any]) -> str:
        """Encrypt message content"""
        content_str = json.dumps(content)
        return self.fernet.encrypt(content_str.encode()).decode()
    
    def decrypt_content(self, encrypted_content: str) -> Dict[str, Any]:
        """Decrypt message content"""
        decrypted_str = self.fernet.decrypt(encrypted_content.encode()).decode()
        return json.loads(decrypted_str)


class MessageRouter:
    """Message routing and delivery system with priority handling"""
    
    def __init__(self, communication_dir: str):
        self.communication_dir = communication_dir
        self.routing_table: Dict[str, str] = {}
        self.priority_queues: Dict[MessagePriority, List[Message]] = {
            priority: [] for priority in MessagePriority
        }
        
    def register_agent(self, agent_id: str, channel_path: str):
        """Register an agent's communication channel"""
        self.routing_table[agent_id] = channel_path
    
    def route_message(self, message: Message) -> bool:
        """Route message to appropriate destination with priority handling"""
        try:
            # Add to priority queue
            self.priority_queues[message.priority].append(message)
            
            # Process queues by priority
            return self._process_priority_queues()
            
        except Exception as e:
            print(f"Routing error: {e}")
            return False
    
    def _process_priority_queues(self) -> bool:
        """Process messages by priority order"""
        for priority in MessagePriority:
            while self.priority_queues[priority]:
                message = self.priority_queues[priority].pop(0)
                if not self._deliver_message(message):
                    # Re-queue for retry if not exceeded max retries
                    if message.retry_count < message.max_retries:
                        message.retry_count += 1
                        self.priority_queues[priority].append(message)
                    else:
                        message.status = MessageStatus.FAILED
        return True
    
    def _deliver_message(self, message: Message) -> bool:
        """Deliver message to target agent"""
        try:
            # Create message file
            filename = f"msg_{message.msg_type.value.lower()}_{message.from_agent}_to_{message.to_agent}_{int(time.time())}.txt"
            filepath = os.path.join(self.communication_dir, filename)
            
            # Format message content
            message_content = self._format_message_for_file(message)
            
            # Write with file locking
            with open(filepath, 'w') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                f.write(message_content)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            
            message.status = MessageStatus.DELIVERED
            return True
            
        except Exception as e:
            print(f"Delivery error: {e}")
            return False
    
    def _format_message_for_file(self, message: Message) -> str:
        """Format message for file-based communication"""
        content = f"MESSAGE PROTOCOL v2.0\n"
        content += f"===================\n"
        content += f"MSG_ID: {message.msg_id}\n"
        content += f"TYPE: {message.msg_type.value}\n"
        content += f"FROM: {message.from_agent}\n"
        content += f"TO: {message.to_agent}\n"
        content += f"TIMESTAMP: {message.timestamp}\n"
        content += f"PRIORITY: {message.priority.name}\n"
        content += f"STATUS: {message.status.value}\n"
        content += f"REQUIRES_RESPONSE: {message.requires_response}\n"
        
        if message.correlation_id:
            content += f"CORRELATION_ID: {message.correlation_id}\n"
        
        content += f"CHECKSUM: {message.checksum}\n"
        content += f"RETRY_COUNT: {message.retry_count}\n"
        
        content += f"\nCONTENT:\n"
        content += f"--------\n"
        content += json.dumps(message.content, indent=2)
        
        return content


class CollaborationProtocol:
    """High-level collaboration protocol manager"""
    
    def __init__(self, agent_id: str, communication_dir: str):
        self.agent_id = agent_id
        self.communication_dir = communication_dir
        self.validator = MessageValidator()
        self.router = MessageRouter(communication_dir)
        self.message_history: List[Message] = []
        self.active_collaborations: Dict[str, Dict] = {}
        
    def send_heartbeat(self, target_agent: str) -> bool:
        """Send heartbeat message to maintain connection"""
        message = self._create_message(
            msg_type=MessageType.HEARTBEAT,
            to_agent=target_agent,
            content={"status": "alive", "timestamp": datetime.now().isoformat()},
            priority=MessagePriority.HIGH
        )
        return self._send_message(message)
    
    def request_collaboration(self, target_agent: str, task_description: str, required_capabilities: List[str]) -> bool:
        """Request collaboration with another agent"""
        message = self._create_message(
            msg_type=MessageType.COLLABORATION_REQUEST,
            to_agent=target_agent,
            content={
                "task_description": task_description,
                "required_capabilities": required_capabilities,
                "proposed_roles": {
                    "requester": self.agent_id,
                    "collaborator": target_agent
                }
            },
            requires_response=True,
            priority=MessagePriority.HIGH
        )
        return self._send_message(message)
    
    def request_review(self, target_agent: str, review_type: str, content_reference: str) -> bool:
        """Request code/work review from another agent"""
        message = self._create_message(
            msg_type=MessageType.REVIEW_REQUIRED,
            to_agent=target_agent,
            content={
                "review_type": review_type,
                "content_reference": content_reference,
                "requestor": self.agent_id,
                "priority_level": "high"
            },
            requires_response=True,
            priority=MessagePriority.HIGH
        )
        return self._send_message(message)
    
    def grant_approval(self, target_agent: str, approval_type: str, details: Dict[str, Any]) -> bool:
        """Grant approval for requested action/implementation"""
        message = self._create_message(
            msg_type=MessageType.APPROVAL_GRANTED,
            to_agent=target_agent,
            content={
                "approval_type": approval_type,
                "approved_by": self.agent_id,
                "details": details,
                "conditions": details.get("conditions", [])
            },
            priority=MessagePriority.HIGH
        )
        return self._send_message(message)
    
    def delegate_task(self, target_agent: str, task_details: Dict[str, Any]) -> bool:
        """Delegate a task to another agent"""
        message = self._create_message(
            msg_type=MessageType.TASK_DELEGATION,
            to_agent=target_agent,
            content={
                "task_id": task_details.get("task_id"),
                "task_description": task_details.get("description"),
                "requirements": task_details.get("requirements", []),
                "deadline": task_details.get("deadline"),
                "delegated_by": self.agent_id
            },
            requires_response=True,
            priority=MessagePriority.NORMAL
        )
        return self._send_message(message)
    
    def _create_message(self, msg_type: MessageType, to_agent: str, content: Dict[str, Any], 
                       requires_response: bool = False, priority: MessagePriority = MessagePriority.NORMAL) -> Message:
        """Create a new message with proper metadata"""
        msg_id = f"{self.agent_id}_{int(time.time())}_{hash(str(content)) % 10000}"
        
        return Message(
            msg_id=msg_id,
            msg_type=msg_type,
            from_agent=self.agent_id,
            to_agent=to_agent,
            content=content,
            timestamp=datetime.now().isoformat(),
            priority=priority,
            requires_response=requires_response
        )
    
    def _send_message(self, message: Message) -> bool:
        """Send message through the protocol stack"""
        try:
            # Validate message
            is_valid, error_msg = self.validator.validate_message(message)
            if not is_valid:
                print(f"Message validation failed: {error_msg}")
                return False
            
            # Route message
            success = self.router.route_message(message)
            if success:
                self.message_history.append(message)
                message.status = MessageStatus.SENT
            
            return success
            
        except Exception as e:
            print(f"Send message error: {e}")
            return False


# Usage example and factory functions
def create_collaboration_protocol(agent_id: str, communication_dir: str) -> CollaborationProtocol:
    """Factory function to create a collaboration protocol instance"""
    return CollaborationProtocol(agent_id, communication_dir)


def create_secure_message(from_agent: str, to_agent: str, msg_type: MessageType, 
                         content: Dict[str, Any], encrypt: bool = False) -> Message:
    """Factory function to create secure messages"""
    validator = MessageValidator()
    
    if encrypt:
        encrypted_content = validator.encrypt_content(content)
        content = {"encrypted": encrypted_content}
    
    msg_id = f"{from_agent}_{int(time.time())}_{hash(str(content)) % 10000}"
    
    return Message(
        msg_id=msg_id,
        msg_type=msg_type,
        from_agent=from_agent,
        to_agent=to_agent,
        content=content,
        timestamp=datetime.now().isoformat()
    )


if __name__ == "__main__":
    # Example usage
    protocol = create_collaboration_protocol("agent_black", "/home/patrick/projects/giano/chat")
    
    # Send a collaboration request
    protocol.request_collaboration(
        target_agent="agent_white",
        task_description="Implement enhanced collaborative framework",
        required_capabilities=["code_review", "testing", "validation"]
    )
    
    # Send a review request
    protocol.request_review(
        target_agent="agent_white",
        review_type="code_implementation",
        content_reference="message_protocol.py"
    )
