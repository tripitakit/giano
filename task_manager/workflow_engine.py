"""
Workflow Engine Module for AI Agent Collaboration System
Advanced task orchestration, pipeline processing, and dependency management

Author: Agent Black (Primary Architect)
Quality Review: Agent White (QA Specialist)  
Version: 3.0 - Advanced Collaboration Framework
Dependencies: message_protocol.py, synchronization.py
"""

import time
import json
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, Future
import uuid

from message_protocol import (
    Message, MessageType, Priority, CollaborationProtocol, 
    MessageValidator, MessageRouter
)
from synchronization import (
    DistributedCoordinator, ResourceCoordinator, DeadlockDetector,
    LockState, CoordinationStrategy
)


class TaskStatus(Enum):
    """Status values for workflow tasks"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class WorkflowStatus(Enum):
    """Status values for entire workflows"""
    CREATED = "created"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ExecutionStrategy(Enum):
    """Strategies for task execution"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINE = "pipeline"
    ADAPTIVE = "adaptive"


@dataclass
class TaskDefinition:
    """Defines a single task in a workflow"""
    task_id: str
    name: str
    description: str
    function: Callable
    dependencies: Set[str] = field(default_factory=set)
    required_resources: List[str] = field(default_factory=list)
    priority: Priority = Priority.NORMAL
    timeout: float = 300.0  # 5 minutes default
    retry_count: int = 0
    max_retries: int = 3
    assigned_agent: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    
    def is_ready(self, completed_tasks: Set[str]) -> bool:
        """Check if task is ready to execute (all dependencies completed)"""
        return self.dependencies.issubset(completed_tasks)
    
    def get_execution_duration(self) -> float:
        """Get actual execution duration"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return time.time() - self.started_at
        return 0.0


@dataclass 
class WorkflowDefinition:
    """Defines a complete workflow with tasks and dependencies"""
    workflow_id: str
    name: str
    description: str
    tasks: Dict[str, TaskDefinition] = field(default_factory=dict)
    execution_strategy: ExecutionStrategy = ExecutionStrategy.ADAPTIVE
    status: WorkflowStatus = WorkflowStatus.CREATED
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    created_by: Optional[str] = None
    assigned_agents: Set[str] = field(default_factory=set)
    max_concurrent_tasks: int = 5
    total_timeout: float = 3600.0  # 1 hour default
    progress: float = 0.0
    
    def add_task(self, task: TaskDefinition):
        """Add a task to the workflow"""
        self.tasks[task.task_id] = task
        if task.assigned_agent:
            self.assigned_agents.add(task.assigned_agent)
    
    def add_dependency(self, task_id: str, dependency_id: str):
        """Add dependency between tasks"""
        if task_id in self.tasks and dependency_id in self.tasks:
            self.tasks[task_id].dependencies.add(dependency_id)
    
    def get_ready_tasks(self, completed_tasks: Set[str]) -> List[TaskDefinition]:
        """Get tasks that are ready to execute"""
        ready = []
        for task in self.tasks.values():
            if (task.status == TaskStatus.PENDING and 
                task.is_ready(completed_tasks)):
                ready.append(task)
        return sorted(ready, key=lambda t: t.priority.value, reverse=True)
    
    def calculate_progress(self) -> float:
        """Calculate workflow completion progress"""
        if not self.tasks:
            return 0.0
        
        completed = sum(1 for task in self.tasks.values() 
                       if task.status == TaskStatus.COMPLETED)
        return (completed / len(self.tasks)) * 100.0
    
    def get_dependency_graph(self) -> Dict[str, Set[str]]:
        """Get task dependency graph"""
        return {task_id: task.dependencies.copy() 
                for task_id, task in self.tasks.items()}
    
    def validate_dependencies(self) -> Tuple[bool, List[str]]:
        """Validate workflow for circular dependencies"""
        # Topological sort to detect cycles
        graph = self.get_dependency_graph()
        in_degree = defaultdict(int)
        
        # Calculate in-degrees
        for task_id in graph:
            for dep in graph[task_id]:
                in_degree[dep] += 1
        
        # Queue for zero in-degree nodes
        queue = deque([task_id for task_id in graph if in_degree[task_id] == 0])
        processed = []
        
        while queue:
            current = queue.popleft()
            processed.append(current)
            
            for task_id, deps in graph.items():
                if current in deps:
                    in_degree[task_id] -= 1
                    if in_degree[task_id] == 0:
                        queue.append(task_id)
        
        if len(processed) != len(graph):
            # Circular dependency detected
            remaining = set(graph.keys()) - set(processed)
            return False, list(remaining)
        
        return True, []


class TaskExecutor:
    """Executes individual tasks with resource management"""
    
    def __init__(self, agent_id: str, coordinator: DistributedCoordinator):
        self.agent_id = agent_id
        self.coordinator = coordinator
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.active_executions: Dict[str, Future] = {}
        
    def execute_task(self, task: TaskDefinition, workflow_id: str) -> bool:
        """Execute a single task with resource management"""
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        
        try:
            # Acquire required resources
            acquired_resources = []
            for resource in task.required_resources:
                if self.coordinator.resource_coordinator.request_lock(
                    resource, task.priority, task.timeout
                ):
                    acquired_resources.append(resource)
                else:
                    # Failed to acquire resource - rollback
                    for acquired in acquired_resources:
                        self.coordinator.resource_coordinator.release_lock(acquired)
                    task.status = TaskStatus.BLOCKED
                    task.error = f"Failed to acquire resource: {resource}"
                    return False
            
            # Execute the task function
            future = self.executor.submit(self._execute_with_timeout, task)
            self.active_executions[task.task_id] = future
            
            # Wait for completion or timeout
            try:
                result = future.result(timeout=task.timeout)
                task.result = result
                task.status = TaskStatus.COMPLETED
                task.completed_at = time.time()
                task.execution_time = task.get_execution_duration()
                
                # Notify completion
                self._notify_task_completion(task, workflow_id, True)
                return True
                
            except Exception as e:
                task.error = str(e)
                task.status = TaskStatus.FAILED
                task.completed_at = time.time()
                
                # Retry logic
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    task.status = TaskStatus.PENDING
                    self._notify_task_retry(task, workflow_id)
                    return False
                else:
                    self._notify_task_completion(task, workflow_id, False)
                    return False
                    
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            task.completed_at = time.time()
            return False
            
        finally:
            # Release all acquired resources
            for resource in acquired_resources:
                self.coordinator.resource_coordinator.release_lock(resource)
            
            # Clean up execution tracking
            if task.task_id in self.active_executions:
                del self.active_executions[task.task_id]
    
    def _execute_with_timeout(self, task: TaskDefinition) -> Any:
        """Execute task function with proper error handling"""
        try:
            if callable(task.function):
                return task.function()
            else:
                # If function is a string, treat as command
                import subprocess
                result = subprocess.run(
                    task.function, shell=True, capture_output=True, text=True
                )
                if result.returncode == 0:
                    return result.stdout
                else:
                    raise Exception(f"Command failed: {result.stderr}")
        except Exception as e:
            raise Exception(f"Task execution failed: {str(e)}")
    
    def _notify_task_completion(self, task: TaskDefinition, workflow_id: str, success: bool):
        """Notify other agents about task completion"""
        status = "completed" if success else "failed"
        content = {
            "workflow_id": workflow_id,
            "task_id": task.task_id,
            "status": status,
            "execution_time": task.execution_time,
            "result": str(task.result) if task.result else None,
            "error": task.error
        }
        
        message = Message(
            message_type=MessageType.STATUS_UPDATE,
            from_agent=self.agent_id,
            to_agent="broadcast",
            content=content,
            priority=Priority.NORMAL
        )
        
        self.coordinator.collaboration_protocol.router.send_message(message)
    
    def _notify_task_retry(self, task: TaskDefinition, workflow_id: str):
        """Notify about task retry"""
        content = {
            "workflow_id": workflow_id,
            "task_id": task.task_id,
            "retry_count": task.retry_count,
            "max_retries": task.max_retries
        }
        
        message = Message(
            message_type=MessageType.STATUS_UPDATE,
            from_agent=self.agent_id,
            to_agent="broadcast",
            content=content,
            priority=Priority.NORMAL
        )
        
        self.coordinator.collaboration_protocol.router.send_message(message)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self.active_executions:
            future = self.active_executions[task_id]
            cancelled = future.cancel()
            if cancelled:
                del self.active_executions[task_id]
            return cancelled
        return False
    
    def get_active_tasks(self) -> List[str]:
        """Get list of currently executing task IDs"""
        return list(self.active_executions.keys())


class WorkflowScheduler:
    """Schedules and manages workflow execution"""
    
    def __init__(self, agent_id: str, coordinator: DistributedCoordinator):
        self.agent_id = agent_id
        self.coordinator = coordinator
        self.task_executor = TaskExecutor(agent_id, coordinator)
        self.active_workflows: Dict[str, WorkflowDefinition] = {}
        self.completed_tasks: Dict[str, Set[str]] = defaultdict(set)
        self.scheduler_lock = threading.Lock()
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        
    def submit_workflow(self, workflow: WorkflowDefinition) -> bool:
        """Submit a workflow for execution"""
        # Validate workflow
        is_valid, cycles = workflow.validate_dependencies()
        if not is_valid:
            raise ValueError(f"Circular dependencies detected: {cycles}")
        
        with self.scheduler_lock:
            workflow.status = WorkflowStatus.SCHEDULED
            self.active_workflows[workflow.workflow_id] = workflow
            self.completed_tasks[workflow.workflow_id] = set()
        
        # Notify other agents about workflow submission
        self._notify_workflow_status(workflow, "submitted")
        return True
    
    def start_scheduler(self):
        """Start the workflow scheduler"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
    
    def stop_scheduler(self):
        """Stop the workflow scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                with self.scheduler_lock:
                    for workflow_id, workflow in self.active_workflows.items():
                        if workflow.status == WorkflowStatus.SCHEDULED:
                            workflow.status = WorkflowStatus.RUNNING
                            workflow.started_at = time.time()
                            self._notify_workflow_status(workflow, "started")
                        
                        if workflow.status == WorkflowStatus.RUNNING:
                            self._execute_workflow_step(workflow)
                
                time.sleep(1.0)  # Scheduler polling interval
                
            except Exception as e:
                print(f"Scheduler error: {e}")
    
    def _execute_workflow_step(self, workflow: WorkflowDefinition):
        """Execute one step of workflow processing"""
        completed = self.completed_tasks[workflow.workflow_id]
        ready_tasks = workflow.get_ready_tasks(completed)
        
        # Check for completion
        if all(task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] 
               for task in workflow.tasks.values()):
            self._complete_workflow(workflow)
            return
        
        # Execute ready tasks based on strategy
        if workflow.execution_strategy == ExecutionStrategy.SEQUENTIAL:
            self._execute_sequential(workflow, ready_tasks)
        elif workflow.execution_strategy == ExecutionStrategy.PARALLEL:
            self._execute_parallel(workflow, ready_tasks)
        elif workflow.execution_strategy == ExecutionStrategy.PIPELINE:
            self._execute_pipeline(workflow, ready_tasks)
        else:  # ADAPTIVE
            self._execute_adaptive(workflow, ready_tasks)
        
        # Update progress
        workflow.progress = workflow.calculate_progress()
    
    def _execute_sequential(self, workflow: WorkflowDefinition, ready_tasks: List[TaskDefinition]):
        """Execute tasks sequentially"""
        active_tasks = self.task_executor.get_active_tasks()
        
        if not active_tasks and ready_tasks:
            # Execute highest priority ready task
            task = ready_tasks[0]
            task.status = TaskStatus.READY
            self.task_executor.execute_task(task, workflow.workflow_id)
    
    def _execute_parallel(self, workflow: WorkflowDefinition, ready_tasks: List[TaskDefinition]):
        """Execute tasks in parallel"""
        active_count = len(self.task_executor.get_active_tasks())
        max_concurrent = workflow.max_concurrent_tasks
        
        for task in ready_tasks:
            if active_count >= max_concurrent:
                break
            
            task.status = TaskStatus.READY
            self.task_executor.execute_task(task, workflow.workflow_id)
            active_count += 1
    
    def _execute_pipeline(self, workflow: WorkflowDefinition, ready_tasks: List[TaskDefinition]):
        """Execute tasks in pipeline fashion"""
        # Pipeline execution - start next stage when previous is complete
        # This is a simplified implementation
        self._execute_parallel(workflow, ready_tasks)
    
    def _execute_adaptive(self, workflow: WorkflowDefinition, ready_tasks: List[TaskDefinition]):
        """Adaptive execution strategy"""
        # Choose strategy based on workflow characteristics
        if len(workflow.tasks) <= 3:
            self._execute_sequential(workflow, ready_tasks)
        else:
            self._execute_parallel(workflow, ready_tasks)
    
    def _complete_workflow(self, workflow: WorkflowDefinition):
        """Complete workflow and cleanup"""
        workflow.completed_at = time.time()
        
        # Determine final status
        failed_tasks = [task for task in workflow.tasks.values() 
                       if task.status == TaskStatus.FAILED]
        
        if failed_tasks:
            workflow.status = WorkflowStatus.FAILED
        else:
            workflow.status = WorkflowStatus.COMPLETED
        
        workflow.progress = 100.0
        self._notify_workflow_status(workflow, "completed")
    
    def _notify_workflow_status(self, workflow: WorkflowDefinition, event: str):
        """Notify other agents about workflow status changes"""
        content = {
            "workflow_id": workflow.workflow_id,
            "status": workflow.status.value,
            "progress": workflow.progress,
            "event": event,
            "agent_id": self.agent_id
        }
        
        message = Message(
            message_type=MessageType.STATUS_UPDATE,
            from_agent=self.agent_id,
            to_agent="broadcast",
            content=content,
            priority=Priority.NORMAL
        )
        
        self.coordinator.collaboration_protocol.router.send_message(message)
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed workflow status"""
        with self.scheduler_lock:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                return None
            
            return {
                "workflow_id": workflow.workflow_id,
                "name": workflow.name,
                "status": workflow.status.value,
                "progress": workflow.progress,
                "created_at": workflow.created_at,
                "started_at": workflow.started_at,
                "completed_at": workflow.completed_at,
                "total_tasks": len(workflow.tasks),
                "completed_tasks": len(self.completed_tasks[workflow_id]),
                "active_tasks": len(self.task_executor.get_active_tasks()),
                "execution_strategy": workflow.execution_strategy.value
            }
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        with self.scheduler_lock:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                return False
            
            # Cancel all active tasks
            for task_id in self.task_executor.get_active_tasks():
                self.task_executor.cancel_task(task_id)
            
            # Update workflow status
            workflow.status = WorkflowStatus.CANCELLED
            workflow.completed_at = time.time()
            
            self._notify_workflow_status(workflow, "cancelled")
            return True


class WorkflowEngine:
    """Main workflow engine orchestrating all components"""
    
    def __init__(self, agent_id: str, communication_dir: str):
        self.agent_id = agent_id
        self.coordinator = DistributedCoordinator(agent_id, communication_dir)
        self.scheduler = WorkflowScheduler(agent_id, self.coordinator)
        self.workflow_templates: Dict[str, WorkflowDefinition] = {}
        self.performance_metrics: Dict[str, Any] = {}
        
    def create_workflow(self, name: str, description: str, 
                       execution_strategy: ExecutionStrategy = ExecutionStrategy.ADAPTIVE) -> WorkflowDefinition:
        """Create a new workflow definition"""
        workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"
        
        workflow = WorkflowDefinition(
            workflow_id=workflow_id,
            name=name,
            description=description,
            execution_strategy=execution_strategy,
            created_by=self.agent_id
        )
        
        return workflow
    
    def add_task_to_workflow(self, workflow: WorkflowDefinition, name: str, 
                           description: str, function: Callable, 
                           dependencies: List[str] = None,
                           required_resources: List[str] = None,
                           priority: Priority = Priority.NORMAL,
                           assigned_agent: str = None) -> str:
        """Add a task to a workflow"""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        task = TaskDefinition(
            task_id=task_id,
            name=name,
            description=description,
            function=function,
            dependencies=set(dependencies or []),
            required_resources=required_resources or [],
            priority=priority,
            assigned_agent=assigned_agent or self.agent_id
        )
        
        workflow.add_task(task)
        return task_id
    
    def submit_workflow(self, workflow: WorkflowDefinition) -> bool:
        """Submit workflow for execution"""
        return self.scheduler.submit_workflow(workflow)
    
    def start_engine(self):
        """Start the workflow engine"""
        self.scheduler.start_scheduler()
    
    def stop_engine(self):
        """Stop the workflow engine"""
        self.scheduler.stop_scheduler()
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get comprehensive engine status"""
        return {
            "agent_id": self.agent_id,
            "active_workflows": len(self.scheduler.active_workflows),
            "system_health": self.coordinator.health_check(),
            "performance_metrics": self.performance_metrics.copy()
        }


# Factory function for easy instantiation
def create_workflow_engine(agent_id: str, communication_dir: str) -> WorkflowEngine:
    """Create a complete workflow engine for an agent"""
    return WorkflowEngine(agent_id, communication_dir)


# Example usage and demonstration
if __name__ == "__main__":
    # Example workflow creation and execution
    engine = create_workflow_engine("agent1", "/tmp/collaboration")
    
    # Create a sample workflow
    workflow = engine.create_workflow(
        "Data Processing Pipeline",
        "Process data through multiple stages",
        ExecutionStrategy.PIPELINE
    )
    
    # Add tasks with dependencies
    task1_id = engine.add_task_to_workflow(
        workflow, "Load Data", "Load input data",
        lambda: print("Loading data..."),
        required_resources=["data_file.csv"]
    )
    
    task2_id = engine.add_task_to_workflow(
        workflow, "Process Data", "Process loaded data",  
        lambda: print("Processing data..."),
        dependencies=[task1_id],
        required_resources=["processing_engine"]
    )
    
    task3_id = engine.add_task_to_workflow(
        workflow, "Save Results", "Save processed results",
        lambda: print("Saving results..."),
        dependencies=[task2_id],
        required_resources=["output_file.csv"]
    )
    
    print("Workflow created successfully!")
    print(f"Workflow ID: {workflow.workflow_id}")
    print(f"Total tasks: {len(workflow.tasks)}")
    
    # Submit and start
    engine.submit_workflow(workflow)
    engine.start_engine()
    
    print("Workflow engine started!")
