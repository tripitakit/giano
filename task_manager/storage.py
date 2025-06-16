"""
Task Management System - Storage Module
Handles persistence and retrieval of tasks
Collaborative implementation between Agent 1 (writer) and Agent 2 (reviewer/tester)
"""

import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from task import Task


class TaskStorage:
    """Handles task persistence using JSON file storage"""
    
    def __init__(self, storage_file: str = "tasks.json"):
        self.storage_file = storage_file
        self.tasks: Dict[str, Task] = {}
        self.load_tasks()
    
    def load_tasks(self) -> bool:
        """Load tasks from storage file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    
                self.tasks = {}
                for task_data in data.get("tasks", []):
                    task = Task.from_dict(task_data)
                    self.tasks[task.task_id] = task
                    
                return True
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self.tasks = {}
            
        return False
    
    def save_tasks(self) -> bool:
        """Save tasks to storage file"""
        try:
            data = {
                "saved_at": datetime.now().isoformat(),
                "task_count": len(self.tasks),
                "tasks": [task.to_dict() for task in self.tasks.values()]
            }
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving tasks: {e}")
            return False
    
    def create_task(self, task: Task) -> bool:
        """Create a new task"""
        if task.task_id in self.tasks:
            return False  # Task already exists
            
        self.tasks[task.task_id] = task
        return self.save_tasks()
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks"""
        return list(self.tasks.values())
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing task"""
        if task_id not in self.tasks:
            return False
            
        task = self.tasks[task_id]
        
        # Update allowed fields
        allowed_fields = ['title', 'description', 'status', 'priority', 
                         'due_date', 'assigned_to', 'tags']
        
        for field, value in updates.items():
            if field in allowed_fields:
                if field == 'due_date' and value:
                    # Handle datetime conversion
                    if isinstance(value, str):
                        value = datetime.fromisoformat(value)
                        
                setattr(task, field, value)
        
        task.updated_at = datetime.now()
        return self.save_tasks()
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        if task_id not in self.tasks:
            return False
            
        del self.tasks[task_id]
        return self.save_tasks()
    
    def search_tasks(self, query: str) -> List[Task]:
        """Search tasks by title or description"""
        query = query.lower()
        results = []
        
        for task in self.tasks.values():
            if (query in task.title.lower() or 
                query in task.description.lower() or
                query in ' '.join(task.tags).lower()):
                results.append(task)
                
        return results
    
    def filter_tasks(self, **filters) -> List[Task]:
        """Filter tasks by various criteria"""
        results = []
        
        for task in self.tasks.values():
            match = True
            
            for field, value in filters.items():
                if hasattr(task, field):
                    task_value = getattr(task, field)
                    
                    if field == 'tags':
                        # Check if any of the filter tags are in task tags
                        if isinstance(value, list):
                            if not any(tag in task.tags for tag in value):
                                match = False
                                break
                        else:
                            if value not in task.tags:
                                match = False
                                break
                    else:
                        if task_value != value:
                            match = False
                            break
            
            if match:
                results.append(task)
                
        return results
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks"""
        return [task for task in self.tasks.values() if task.is_overdue()]
    
    def get_tasks_by_status(self, status: str) -> List[Task]:
        """Get tasks by status"""
        return [task for task in self.tasks.values() if task.status == status]
    
    def get_tasks_by_priority(self, priority: str) -> List[Task]:
        """Get tasks by priority"""
        return [task for task in self.tasks.values() if task.priority == priority]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get task statistics"""
        total_tasks = len(self.tasks)
        
        if total_tasks == 0:
            return {"total_tasks": 0}
        
        status_counts = {}
        priority_counts = {}
        
        for task in self.tasks.values():
            status_counts[task.status] = status_counts.get(task.status, 0) + 1
            priority_counts[task.priority] = priority_counts.get(task.priority, 0) + 1
        
        overdue_count = len(self.get_overdue_tasks())
        
        return {
            "total_tasks": total_tasks,
            "by_status": status_counts,
            "by_priority": priority_counts,
            "overdue_tasks": overdue_count
        }
    
    def backup_tasks(self, backup_file: str) -> bool:
        """Create a backup of all tasks"""
        try:
            data = {
                "backup_created": datetime.now().isoformat(),
                "original_file": self.storage_file,
                "task_count": len(self.tasks),
                "tasks": [task.to_dict() for task in self.tasks.values()]
            }
            
            with open(backup_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False