# AI Agent Collaboration Framework - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Prerequisites
```bash
# Ensure Python 3.8+ is installed
python3 --version

# Install required dependencies
pip install cryptography
```

### 2. Download Framework Files
Copy these files to your project directory:
- `message_protocol.py`
- `synchronization.py` 
- `workflow_engine.py`

### 3. Basic Agent Creation
```python
from workflow_engine import create_workflow_engine

# Create and start an agent
agent = create_workflow_engine("my_agent", "/tmp/collaboration")
agent.start_engine()
```

### 4. Simple Workflow Example
```python
# Create a workflow
workflow = agent.create_workflow("My First Workflow", "Simple example")

# Add a task
def hello_world():
    print("Hello from AI Agent Collaboration Framework!")
    return "success"

task_id = agent.add_task_to_workflow(
    workflow, "Hello Task", "My first task", hello_world
)

# Execute
agent.submit_workflow(workflow)
```

## 🎯 Core Concepts

### Agents
```python
# Each agent has a unique ID and communication directory
agent1 = create_workflow_engine("agent1", "/path/to/comm")
agent2 = create_workflow_engine("agent2", "/path/to/comm")
```

### Workflows
```python
# Workflows contain multiple tasks with dependencies
workflow = agent.create_workflow(
    name="Data Processing",
    description="Process data pipeline", 
    execution_strategy=ExecutionStrategy.PARALLEL
)
```

### Tasks
```python
# Tasks are functions with dependencies and resource requirements
task_id = agent.add_task_to_workflow(
    workflow,
    name="Process Data",
    description="Process the input data",
    function=my_processing_function,
    dependencies=["previous_task_id"],
    required_resources=["database", "cpu_core"],
    priority=Priority.HIGH
)
```

### Communication
```python
from message_protocol import create_collaboration_protocol

# Agents communicate through structured messages
protocol = create_collaboration_protocol("agent1", "/path/to/comm")
protocol.send_heartbeat("agent2")
protocol.request_collaboration("agent2", "Joint task", ["capability1"])
```

### Resource Management
```python
from synchronization import create_synchronization_system

# Coordinate shared resources between agents
coord = create_synchronization_system("agent1", "/path/to/comm")
success = coord.resource_coordinator.request_lock("shared_file")
# ... do work ...
coord.resource_coordinator.release_lock("shared_file")
```

## 📚 Complete Examples

### Single Agent Workflow
```python
#!/usr/bin/env python3
from workflow_engine import create_workflow_engine, ExecutionStrategy
from message_protocol import Priority
import time

# Create agent
agent = create_workflow_engine("data_processor", "/tmp/collaboration")
agent.start_engine()

# Create workflow
workflow = agent.create_workflow(
    "Data Pipeline", 
    "Complete data processing pipeline",
    ExecutionStrategy.SEQUENTIAL
)

# Define tasks
def load_data():
    print("Loading data...")
    time.sleep(1)
    return {"records": 1000}

def process_data():
    print("Processing data...")
    time.sleep(2)
    return {"processed": 1000}

def save_results():
    print("Saving results...")
    time.sleep(0.5)
    return {"saved": True}

# Add tasks with dependencies
task1 = agent.add_task_to_workflow(workflow, "Load", "Load data", load_data)
task2 = agent.add_task_to_workflow(workflow, "Process", "Process data", process_data, dependencies=[task1])
task3 = agent.add_task_to_workflow(workflow, "Save", "Save results", save_results, dependencies=[task2])

# Execute workflow
agent.submit_workflow(workflow)

# Monitor progress
while True:
    status = agent.scheduler.get_workflow_status(workflow.workflow_id)
    if status and status['status'] in ['completed', 'failed']:
        print(f"Workflow {status['status']}!")
        break
    time.sleep(1)

agent.stop_engine()
```

### Multi-Agent Collaboration
```python
#!/usr/bin/env python3
from workflow_engine import create_workflow_engine
from synchronization import create_synchronization_system
from message_protocol import create_collaboration_protocol
import threading
import time

# Create two agents
agent1 = create_workflow_engine("producer", "/tmp/collaboration")
agent2 = create_workflow_engine("consumer", "/tmp/collaboration")

coord1 = create_synchronization_system("producer", "/tmp/collaboration")
coord2 = create_synchronization_system("consumer", "/tmp/collaboration")

agent1.start_engine()
agent2.start_engine()

def producer_workflow():
    workflow = agent1.create_workflow("Produce Data", "Generate data for consumer")
    
    def produce():
        print("Producer: Creating data...")
        time.sleep(1)
        coord1.resource_coordinator.request_lock("shared_data")
        print("Producer: Data ready for consumer")
        return "data_produced"
    
    agent1.add_task_to_workflow(workflow, "Produce", "Create data", produce)
    agent1.submit_workflow(workflow)

def consumer_workflow():
    time.sleep(0.5)  # Wait for producer to start
    workflow = agent2.create_workflow("Consume Data", "Process data from producer")
    
    def consume():
        print("Consumer: Waiting for data...")
        success = coord2.resource_coordinator.request_lock("shared_data", timeout=5)
        if success:
            print("Consumer: Processing data...")
            time.sleep(1)
            coord2.resource_coordinator.release_lock("shared_data")
            return "data_consumed"
        else:
            raise Exception("Data not available")
    
    agent2.add_task_to_workflow(workflow, "Consume", "Process data", consume)
    agent2.submit_workflow(workflow)

# Run both workflows
producer_thread = threading.Thread(target=producer_workflow)
consumer_thread = threading.Thread(target=consumer_workflow)

producer_thread.start()
consumer_thread.start()

producer_thread.join()
consumer_thread.join()

agent1.stop_engine()
agent2.stop_engine()
print("Multi-agent collaboration completed!")
```

## 🛠️ Common Patterns

### Error Handling with Retries
```python
# Configure task with retry logic
task_id = agent.add_task_to_workflow(
    workflow, "Unreliable Task", "Task that may fail", my_function
)
workflow.tasks[task_id].max_retries = 3
workflow.tasks[task_id].timeout = 30.0
```

### Resource Coordination
```python
def task_with_resources():
    # Resources are automatically acquired before task execution
    # and released after completion (or on failure)
    print("Task executing with exclusive resource access")
    return "completed"

# Specify required resources
agent.add_task_to_workflow(
    workflow, "Safe Task", "Task with resource protection", 
    task_with_resources,
    required_resources=["database", "file_system"]
)
```

### Inter-Agent Communication
```python
# Agent 1 requests collaboration
protocol1 = create_collaboration_protocol("agent1", "/tmp/collaboration")
protocol1.request_collaboration("agent2", "Joint analysis", ["data_analysis"])

# Agent 1 requests review
protocol1.request_review("agent2", "code_review", "my_implementation.py")

# Agent 2 grants approval
protocol2 = create_collaboration_protocol("agent2", "/tmp/collaboration")
protocol2.grant_approval("agent1", "implementation", {"status": "approved"})
```

### Progress Monitoring
```python
# Real-time workflow monitoring
def monitor_workflow(agent, workflow_id):
    while True:
        status = agent.scheduler.get_workflow_status(workflow_id)
        if status:
            print(f"Progress: {status['progress']:.1f}% - {status['status']}")
            if status['status'] in ['completed', 'failed', 'cancelled']:
                break
        time.sleep(1)

# System health monitoring  
def check_system_health(coordinator):
    health = coordinator.health_check()
    print(f"System status: {health['system_status']}")
    print(f"Active collaborations: {health['active_collaborations']}")
    print(f"Resource locks: {health['locks_held']}")
```

## ⚡ Performance Tips

1. **Choose the Right Execution Strategy**:
   - `SEQUENTIAL`: For dependent tasks
   - `PARALLEL`: For independent CPU tasks  
   - `PIPELINE`: For streaming workflows
   - `ADAPTIVE`: Let the system decide

2. **Optimize Resource Usage**:
   - Use fine-grained resource names
   - Set appropriate timeouts
   - Release resources promptly

3. **Configure Concurrency**:
   ```python
   workflow.max_concurrent_tasks = 10  # Adjust based on system capacity
   ```

4. **Monitor Performance**:
   ```python
   # Check resource contention
   locks = coordinator.resource_coordinator.get_all_locks_status()
   
   # Monitor task execution times
   for task in workflow.tasks.values():
       print(f"{task.name}: {task.execution_time:.2f}s")
   ```

## 🔧 Troubleshooting

### Common Issues

**Import Errors**:
```bash
pip install cryptography  # Install missing dependencies
```

**Permission Errors**:
```bash
chmod 755 /path/to/communication/directory
```

**Resource Timeouts**:
```python
# Increase timeout values
coordinator.resource_coordinator.request_lock("resource", timeout=60.0)
```

**Deadlock Detection**:
```python
# Check deadlock status
cycle = coordinator.resource_coordinator.deadlock_detector.detect_cycle()
if cycle:
    print(f"Deadlock detected: {cycle}")
```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📖 Next Steps

1. **Run the Tutorial Suite**:
   ```bash
   python3 tutorial_suite.py
   ```

2. **Read the Complete Documentation**:
   - See `DOCUMENTATION.md` for detailed API reference
   - Explore advanced features and configuration options

3. **Build Your Application**:
   - Start with single-agent workflows
   - Add multi-agent coordination as needed
   - Implement your domain-specific tasks

4. **Production Deployment**:
   - Configure proper logging and monitoring
   - Set up persistent storage for communication
   - Implement security measures for production use

## 🆘 Support

- Review the complete documentation in `DOCUMENTATION.md`
- Run interactive tutorials with `tutorial_suite.py`
- Check the source code for implementation details
- Study the example workflows for best practices

---

**🎉 Happy Building with the AI Agent Collaboration Framework!**
