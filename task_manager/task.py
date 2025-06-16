"""
Task Management System - Task Module
Collaborative implementation between Agent 1 (writer) and Agent 2 (reviewer/tester)
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
import uuid


@dataclass
class Task:
    """A task in the task management system"""
    title: str
    description: str = ""
    status: str = "pending"  # pending, in_progress, completed, cancelled
    priority: str = "medium"  # low, medium, high, urgent
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    tags: list = field(default_factory=list)
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        """Validate task data after initialization"""
        if not self.title.strip():
            raise ValueError("Task title cannot be empty")
        
        valid_statuses = ["pending", "in_progress", "completed", "cancelled"]
        if self.status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
            
        valid_priorities = ["low", "medium", "high", "urgent"]
        if self.priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}")
    
    def update_status(self, new_status: str) -> bool:
        """Update task status with validation"""
        valid_statuses = ["pending", "in_progress", "completed", "cancelled"]
        
        if new_status not in valid_statuses:
            return False
            
        self.status = new_status
        self.updated_at = datetime.now()
        return True
    
    def update_priority(self, new_priority: str) -> bool:
        """Update task priority with validation"""
        valid_priorities = ["low", "medium", "high", "urgent"]
        
        if new_priority not in valid_priorities:
            return False
            
        self.priority = new_priority
        self.updated_at = datetime.now()
        return True
    
    def add_tag(self, tag: str) -> bool:
        """Add a tag to the task"""
        if not tag.strip():
            return False
            
        if tag not in self.tags:
            self.tags.append(tag.strip())
            self.updated_at = datetime.now()
            return True
        return False
    
    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the task"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()
            return True
        return False
    
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if self.due_date is None:
            return False
        return datetime.now() > self.due_date and self.status != "completed"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization"""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "assigned_to": self.assigned_to,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary"""
        # Convert datetime strings back to datetime objects
        created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        updated_at = datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        due_date = None
        if data.get("due_date"):
            due_date = datetime.fromisoformat(data["due_date"])
        
        return cls(
            task_id=data.get("task_id", str(uuid.uuid4())),
            title=data["title"],
            description=data.get("description", ""),
            status=data.get("status", "pending"),
            priority=data.get("priority", "medium"),
            created_at=created_at,
            updated_at=updated_at,
            due_date=due_date,
            assigned_to=data.get("assigned_to"),
            tags=data.get("tags", [])
        )
    
    def __str__(self) -> str:
        """String representation of the task"""
        return f"Task({self.task_id[:8]}): {self.title} [{self.status}]"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"Task(id={self.task_id}, title='{self.title}', "
                f"status='{self.status}', priority='{self.priority}')")