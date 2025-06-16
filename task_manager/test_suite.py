#!/usr/bin/env python3
"""
Comprehensive Test Suite for Agent Collaboration System
Created by Agent 2 (Code Reviewer and Tester)
Tests all components: Task, TaskStorage, and AgentCollaborator
"""

import unittest
import tempfile
import os
import json
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch, mock_open

# Import the modules to test
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from task import Task
from storage import TaskStorage
from manager import AgentCollaborator, AgentInfo


class TestTask(unittest.TestCase):
    """Test cases for Task class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.valid_task_data = {
            "title": "Test Task",
            "description": "A test task for unit testing",
            "status": "pending",
            "priority": "medium"
        }
    
    def test_task_creation_valid(self):
        """Test creating a valid task"""
        task = Task(**self.valid_task_data)
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.status, "pending")
        self.assertEqual(task.priority, "medium")
        self.assertIsNotNone(task.task_id)
        self.assertIsInstance(task.created_at, datetime)
    
    def test_task_creation_empty_title(self):
        """Test that empty title raises ValueError"""
        with self.assertRaises(ValueError):
            Task(title="", description="Test")
    
    def test_task_creation_invalid_status(self):
        """Test that invalid status raises ValueError"""
        with self.assertRaises(ValueError):
            Task(title="Test", status="invalid_status")
    
    def test_task_creation_invalid_priority(self):
        """Test that invalid priority raises ValueError"""
        with self.assertRaises(ValueError):
            Task(title="Test", priority="invalid_priority")
    
    def test_update_status_valid(self):
        """Test updating task status with valid value"""
        task = Task(**self.valid_task_data)
        original_updated = task.updated_at
        result = task.update_status("completed")
        self.assertTrue(result)
        self.assertEqual(task.status, "completed")
        self.assertGreater(task.updated_at, original_updated)
    
    def test_update_status_invalid(self):
        """Test updating task status with invalid value"""
        task = Task(**self.valid_task_data)
        result = task.update_status("invalid_status")
        self.assertFalse(result)
        self.assertEqual(task.status, "pending")  # Should remain unchanged
    
    def test_update_priority_valid(self):
        """Test updating task priority with valid value"""
        task = Task(**self.valid_task_data)
        result = task.update_priority("high")
        self.assertTrue(result)
        self.assertEqual(task.priority, "high")
    
    def test_add_tag(self):
        """Test adding tags to task"""
        task = Task(**self.valid_task_data)
        result = task.add_tag("urgent")
        self.assertTrue(result)
        self.assertIn("urgent", task.tags)
        
        # Test adding duplicate tag
        result = task.add_tag("urgent")
        self.assertFalse(result)
        self.assertEqual(task.tags.count("urgent"), 1)
    
    def test_remove_tag(self):
        """Test removing tags from task"""
        task = Task(**self.valid_task_data)
        task.add_tag("test_tag")
        result = task.remove_tag("test_tag")
        self.assertTrue(result)
        self.assertNotIn("test_tag", task.tags)
        
        # Test removing non-existent tag
        result = task.remove_tag("non_existent")
        self.assertFalse(result)
    
    def test_is_overdue(self):
        """Test overdue detection"""
        task = Task(**self.valid_task_data)
        
        # Task with no due date should not be overdue
        self.assertFalse(task.is_overdue())
        
        # Task with future due date should not be overdue
        task.due_date = datetime.now() + timedelta(days=1)
        self.assertFalse(task.is_overdue())
        
        # Task with past due date should be overdue
        task.due_date = datetime.now() - timedelta(days=1)
        self.assertTrue(task.is_overdue())
        
        # Completed task should not be overdue
        task.status = "completed"
        self.assertFalse(task.is_overdue())
    
    def test_to_dict(self):
        """Test task serialization to dictionary"""
        task = Task(**self.valid_task_data)
        task_dict = task.to_dict()
        
        self.assertEqual(task_dict["title"], "Test Task")
        self.assertEqual(task_dict["status"], "pending")
        self.assertIn("task_id", task_dict)
        self.assertIn("created_at", task_dict)
    
    def test_from_dict(self):
        """Test task deserialization from dictionary"""
        task = Task(**self.valid_task_data)
        task_dict = task.to_dict()
        reconstructed_task = Task.from_dict(task_dict)
        
        self.assertEqual(task.title, reconstructed_task.title)
        self.assertEqual(task.status, reconstructed_task.status)
        self.assertEqual(task.task_id, reconstructed_task.task_id)


class TestTaskStorage(unittest.TestCase):
    """Test cases for TaskStorage class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_file = os.path.join(self.temp_dir, "test_tasks.json")
        self.storage = TaskStorage(self.storage_file)
        
        self.sample_task = Task(
            title="Sample Task",
            description="A sample task for testing",
            status="pending",
            priority="medium"
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_create_task(self):
        """Test creating a new task"""
        result = self.storage.create_task(self.sample_task)
        self.assertTrue(result)
        self.assertIn(self.sample_task.task_id, self.storage.tasks)
    
    def test_get_task(self):
        """Test retrieving a task by ID"""
        self.storage.create_task(self.sample_task)
        retrieved_task = self.storage.get_task(self.sample_task.task_id)
        self.assertIsNotNone(retrieved_task)
        self.assertEqual(retrieved_task.title, self.sample_task.title)
    
    def test_get_all_tasks(self):
        """Test retrieving all tasks"""
        self.storage.create_task(self.sample_task)
        all_tasks = self.storage.get_all_tasks()
        self.assertEqual(len(all_tasks), 1)
        self.assertEqual(all_tasks[0].task_id, self.sample_task.task_id)
    
    def test_update_task(self):
        """Test updating an existing task"""
        self.storage.create_task(self.sample_task)
        updates = {"title": "Updated Task", "status": "in_progress"}
        result = self.storage.update_task(self.sample_task.task_id, updates)
        self.assertTrue(result)
        
        updated_task = self.storage.get_task(self.sample_task.task_id)
        self.assertEqual(updated_task.title, "Updated Task")
        self.assertEqual(updated_task.status, "in_progress")
    
    def test_delete_task(self):
        """Test deleting a task"""
        self.storage.create_task(self.sample_task)
        result = self.storage.delete_task(self.sample_task.task_id)
        self.assertTrue(result)
        self.assertNotIn(self.sample_task.task_id, self.storage.tasks)
    
    def test_search_tasks(self):
        """Test searching tasks"""
        self.storage.create_task(self.sample_task)
        search_results = self.storage.search_tasks("sample")
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].task_id, self.sample_task.task_id)
    
    def test_filter_tasks(self):
        """Test filtering tasks"""
        self.storage.create_task(self.sample_task)
        filtered_tasks = self.storage.filter_tasks(status="pending")
        self.assertEqual(len(filtered_tasks), 1)
        self.assertEqual(filtered_tasks[0].task_id, self.sample_task.task_id)
    
    def test_get_statistics(self):
        """Test getting task statistics"""
        self.storage.create_task(self.sample_task)
        stats = self.storage.get_statistics()
        self.assertEqual(stats["total_tasks"], 1)
        self.assertIn("by_status", stats)
        self.assertIn("by_priority", stats)
    
    def test_backup_tasks(self):
        """Test creating task backup"""
        self.storage.create_task(self.sample_task)
        backup_file = os.path.join(self.temp_dir, "backup_tasks.json")
        result = self.storage.backup_tasks(backup_file)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(backup_file))


class TestAgentCollaborator(unittest.TestCase):
    """Test cases for AgentCollaborator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        # Create a temporary config file
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        config_data = {
            "communication_dir": self.temp_dir,
            "storage_file": "test_tasks.json",
            "backup_dir": "test_backups",
            "handshake_timeout": 300,
            "discovery_interval": 1,
            "max_communication_files": 100,
            "agent_id_pattern": "^agent[1-9]\\d*$"
        }
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f)
            
        self.agent = AgentCollaborator(
            agent_id="agent1",
            role="test_role",
            capabilities=["testing", "validation"],
            config_file=self.config_file
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.agent_id, "agent1")
        self.assertEqual(self.agent.role, "test_role")
        self.assertEqual(self.agent.status, "INITIALIZING")
        self.assertFalse(self.agent.handshake_complete)
    
    def test_discover_agents(self):
        """Test agent discovery"""
        # Create test communication files
        test_file = os.path.join(self.temp_dir, "01_agent1_discovery.txt")
        with open(test_file, 'w') as f:
            f.write("Test agent communication")
        
        discovered = self.agent.discover_agents()
        self.assertGreater(len(discovered), 0)
        self.assertTrue(any("agent" in f.lower() for f in discovered))
    
    def test_announce_presence(self):
        """Test agent announcement"""
        filepath = self.agent.announce_presence()
        self.assertTrue(os.path.exists(filepath))
        self.assertEqual(self.agent.status, "ANNOUNCED")
        
        # Verify file content
        with open(filepath, 'r') as f:
            content = f.read()
            self.assertIn("AGENT ANNOUNCEMENT", content)
            self.assertIn(self.agent.agent_id, content)
    
    def test_initiate_handshake(self):
        """Test handshake initiation"""
        result = self.agent.initiate_handshake("target_agent")
        self.assertTrue(result)
        
        # Check if handshake file was created
        handshake_files = [f for f in os.listdir(self.temp_dir) if "handshake" in f]
        self.assertGreater(len(handshake_files), 0)
    
    def test_complete_handshake(self):
        """Test handshake completion"""
        result = self.agent.complete_handshake("partner_agent")
        self.assertTrue(result)
        self.assertTrue(self.agent.handshake_complete)
        self.assertEqual(self.agent.status, "CONNECTED")
    
    def test_get_collaboration_status(self):
        """Test getting collaboration status"""
        status = self.agent.get_collaboration_status()
        self.assertIn("agent_id", status)
        self.assertIn("role", status)
        self.assertIn("status", status)
        self.assertIn("handshake_complete", status)


class TestAgentInfo(unittest.TestCase):
    """Test cases for AgentInfo dataclass"""
    
    def test_agent_info_creation(self):
        """Test creating AgentInfo instance"""
        agent_info = AgentInfo(
            agent_id="agent1",
            role="tester",
            capabilities=["testing"],
            status="active",
            last_seen="2025-06-15T10:00:00",
            communication_channel="/chat"
        )
        
        self.assertEqual(agent_info.agent_id, "agent1")
        self.assertEqual(agent_info.role, "tester")
        self.assertEqual(agent_info.status, "active")


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
