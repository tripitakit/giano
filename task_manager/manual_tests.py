#!/usr/bin/env python3
"""
Agent 2 - Manual Testing Script
Simple validation of all components
"""

def test_task_module():
    """Test the Task module functionality"""
    print("=== Testing Task Module ===")
    try:
        from task import Task
        from datetime import datetime
        
        # Test basic task creation
        task = Task("Test Task", description="A test task")
        print(f"✅ Task created: {task.title}")
        print(f"✅ Task ID: {task.task_id}")
        print(f"✅ Task status: {task.status}")
        
        # Test status update
        result = task.update_status("completed")
        print(f"✅ Status update: {result}, new status: {task.status}")
        
        # Test tag operations
        task.add_tag("test")
        print(f"✅ Tag added: {task.tags}")
        
        # Test serialization
        task_dict = task.to_dict()
        reconstructed = Task.from_dict(task_dict)
        print(f"✅ Serialization works: {reconstructed.title}")
        
        return True
    except Exception as e:
        print(f"❌ Task module error: {e}")
        return False

def test_storage_module():
    """Test the TaskStorage module functionality"""
    print("\n=== Testing Storage Module ===")
    try:
        from storage import TaskStorage
        from task import Task
        import tempfile
        import os
        
        # Create temporary storage
        temp_file = tempfile.mktemp(suffix='.json')
        storage = TaskStorage(temp_file)
        print(f"✅ Storage created: {temp_file}")
        
        # Create and store a task
        task = Task("Storage Test Task", description="Testing storage")
        result = storage.create_task(task)
        print(f"✅ Task stored: {result}")
        
        # Retrieve the task
        retrieved = storage.get_task(task.task_id)
        print(f"✅ Task retrieved: {retrieved.title if retrieved else 'Failed'}")
        
        # Test search
        search_results = storage.search_tasks("Storage")
        print(f"✅ Search results: {len(search_results)} found")
        
        # Test statistics
        stats = storage.get_statistics()
        print(f"✅ Statistics: {stats['total_tasks']} tasks")
        
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        
        return True
    except Exception as e:
        print(f"❌ Storage module error: {e}")
        return False

def test_manager_module():
    """Test the AgentCollaborator module functionality"""
    print("\n=== Testing Manager Module ===")
    try:
        from manager import AgentCollaborator, AgentInfo
        import tempfile
        import shutil
        
        # Create temporary communication directory
        temp_dir = tempfile.mkdtemp()
        
        # Create agent
        agent = AgentCollaborator("test_agent", "tester", ["testing"])
        agent.communication_dir = temp_dir
        print(f"✅ Agent created: {agent.agent_id}")
        
        # Test announcement
        announcement_file = agent.announce_presence()
        print(f"✅ Announcement created: {os.path.basename(announcement_file)}")
        
        # Test status
        status = agent.get_collaboration_status()
        print(f"✅ Agent status: {status['status']}")
        
        # Test handshake
        handshake_result = agent.initiate_handshake("partner")
        print(f"✅ Handshake initiated: {handshake_result}")
        
        # Clean up
        shutil.rmtree(temp_dir)
        
        return True
    except Exception as e:
        print(f"❌ Manager module error: {e}")
        return False

def main():
    """Run all tests"""
    print("Agent 2 - Component Validation")
    print("=" * 40)
    
    results = []
    results.append(test_task_module())
    results.append(test_storage_module())
    results.append(test_manager_module())
    
    print("\n=== TEST SUMMARY ===")
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Review needed.")
        return False

if __name__ == "__main__":
    import sys
    sys.path.append('.')
    main()
