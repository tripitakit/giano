"""
Synchronization Module for AI Agent Collaboration System
Provides deadlock detection, resource locking, and distributed coordination

Author: Agent Black (Primary Architect)
Quality Review: Agent White (QA Specialist)
Version: 2.0 - Enhanced Collaboration Framework
"""

import time
import json
import fcntl
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
from message_protocol import (
    Message, MessageType, Priority, CollaborationProtocol, 
    MessageValidator, MessageRouter
)


class LockState(Enum):
    """States for resource locks"""
    AVAILABLE = "available"
    REQUESTED = "requested"
    GRANTED = "granted"
    RELEASED = "released"
    DEADLOCK_DETECTED = "deadlock_detected"


class CoordinationStrategy(Enum):
    """Strategies for distributed coordination"""
    TIMESTAMP_ORDERING = "timestamp_ordering"
    PRIORITY_BASED = "priority_based"
    ROUND_ROBIN = "round_robin"
    CAPABILITY_BASED = "capability_based"


@dataclass
class ResourceLock:
    """Represents a resource lock in the system"""
    resource_id: str
    owner_agent: Optional[str] = None
    state: LockState = LockState.AVAILABLE
    request_timestamp: float = field(default_factory=time.time)
    grant_timestamp: Optional[float] = None
    expiry_timestamp: Optional[float] = None
    waiters: List[str] = field(default_factory=list)
    priority: Priority = Priority.NORMAL
    
    def is_expired(self) -> bool:
        """Check if lock has expired"""
        if self.expiry_timestamp is None:
            return False
        return time.time() > self.expiry_timestamp
    
    def time_held(self) -> float:
        """Calculate how long lock has been held"""
        if self.grant_timestamp is None:
            return 0.0
        return time.time() - self.grant_timestamp


@dataclass
class DeadlockInfo:
    """Information about detected deadlock"""
    cycle: List[str]  # Agent IDs in deadlock cycle
    resources: List[str]  # Resource IDs involved
    detection_time: float
    resolution_strategy: str
    resolved: bool = False


class DeadlockDetector:
    """Detects and resolves deadlocks in resource allocation"""
    
    def __init__(self, timeout_seconds: float = 30.0):
        self.timeout_seconds = timeout_seconds
        self.wait_for_graph: Dict[str, Set[str]] = defaultdict(set)
        self.resource_owners: Dict[str, str] = {}
        self.lock = threading.Lock()
        
    def add_wait_edge(self, waiting_agent: str, resource_owner: str):
        """Add edge to wait-for graph"""
        with self.lock:
            self.wait_for_graph[waiting_agent].add(resource_owner)
    
    def remove_wait_edge(self, waiting_agent: str, resource_owner: str):
        """Remove edge from wait-for graph"""
        with self.lock:
            if waiting_agent in self.wait_for_graph:
                self.wait_for_graph[waiting_agent].discard(resource_owner)
                if not self.wait_for_graph[waiting_agent]:
                    del self.wait_for_graph[waiting_agent]
    
    def detect_cycle(self) -> Optional[List[str]]:
        """Detect cycles in wait-for graph using DFS"""
        with self.lock:
            visited = set()
            rec_stack = set()
            
            def dfs(node: str, path: List[str]) -> Optional[List[str]]:
                if node in rec_stack:
                    # Found cycle, return cycle path
                    cycle_start = path.index(node)
                    return path[cycle_start:] + [node]
                
                if node in visited:
                    return None
                
                visited.add(node)
                rec_stack.add(node)
                
                for neighbor in self.wait_for_graph.get(node, []):
                    cycle = dfs(neighbor, path + [neighbor])
                    if cycle:
                        return cycle
                
                rec_stack.remove(node)
                return None
            
            for node in self.wait_for_graph:
                if node not in visited:
                    cycle = dfs(node, [node])
                    if cycle:
                        return cycle
            
            return None
    
    def get_deadlock_info(self, cycle: List[str]) -> DeadlockInfo:
        """Create deadlock information from detected cycle"""
        involved_resources = []
        for agent in cycle:
            for resource_id, owner in self.resource_owners.items():
                if owner == agent:
                    involved_resources.append(resource_id)
        
        return DeadlockInfo(
            cycle=cycle,
            resources=involved_resources,
            detection_time=time.time(),
            resolution_strategy="youngest_dies"  # Default strategy
        )


class ResourceCoordinator:
    """Coordinates resource access across agents"""
    
    def __init__(self, agent_id: str, communication_dir: str):
        self.agent_id = agent_id
        self.communication_dir = communication_dir
        self.locks: Dict[str, ResourceLock] = {}
        self.deadlock_detector = DeadlockDetector()
        self.coordination_strategy = CoordinationStrategy.TIMESTAMP_ORDERING
        self.lock_timeout = 60.0  # Default 60 seconds
        self.main_lock = threading.Lock()
        
        # Integration with message protocol
        self.protocol = CollaborationProtocol(agent_id, communication_dir)
        
    def request_lock(self, resource_id: str, priority: Priority = Priority.NORMAL, 
                    timeout: float = None) -> bool:
        """Request exclusive access to a resource"""
        timeout = timeout or self.lock_timeout
        request_time = time.time()
        
        with self.main_lock:
            if resource_id not in self.locks:
                self.locks[resource_id] = ResourceLock(resource_id)
            
            lock = self.locks[resource_id]
            
            # Check if already owned by this agent
            if lock.owner_agent == self.agent_id:
                return True
            
            # Check if available
            if lock.state == LockState.AVAILABLE or lock.is_expired():
                return self._grant_lock(resource_id, priority, timeout)
            
            # Add to waiters and send lock request message
            if self.agent_id not in lock.waiters:
                lock.waiters.append(self.agent_id)
            
            # Update deadlock detector
            if lock.owner_agent:
                self.deadlock_detector.add_wait_edge(self.agent_id, lock.owner_agent)
            
            lock.state = LockState.REQUESTED
        
        # Send lock request message to other agents
        self._broadcast_lock_request(resource_id, priority)
        
        # Wait for lock or timeout
        return self._wait_for_lock(resource_id, request_time + timeout)
    
    def release_lock(self, resource_id: str) -> bool:
        """Release a resource lock"""
        with self.main_lock:
            if resource_id not in self.locks:
                return False
            
            lock = self.locks[resource_id]
            
            if lock.owner_agent != self.agent_id:
                return False
            
            # Update deadlock detector
            for waiter in lock.waiters:
                self.deadlock_detector.remove_wait_edge(waiter, self.agent_id)
            
            # Release the lock
            lock.owner_agent = None
            lock.state = LockState.RELEASED
            lock.grant_timestamp = None
            lock.expiry_timestamp = None
        
        # Broadcast lock release
        self._broadcast_lock_release(resource_id)
        
        # Grant to next waiter if any
        self._grant_to_next_waiter(resource_id)
        
        return True
    
    def _grant_lock(self, resource_id: str, priority: Priority, timeout: float) -> bool:
        """Grant lock to this agent"""
        lock = self.locks[resource_id]
        lock.owner_agent = self.agent_id
        lock.state = LockState.GRANTED
        lock.grant_timestamp = time.time()
        lock.expiry_timestamp = time.time() + timeout
        lock.priority = priority
        
        # Broadcast lock granted message
        self._broadcast_lock_granted(resource_id)
        return True
    
    def _grant_to_next_waiter(self, resource_id: str):
        """Grant lock to next waiter based on coordination strategy"""
        lock = self.locks[resource_id]
        
        if not lock.waiters:
            lock.state = LockState.AVAILABLE
            return
        
        next_agent = None
        
        if self.coordination_strategy == CoordinationStrategy.TIMESTAMP_ORDERING:
            # Grant to oldest request (FIFO)
            next_agent = lock.waiters[0]
        elif self.coordination_strategy == CoordinationStrategy.PRIORITY_BASED:
            # Grant to highest priority (would need priority tracking per waiter)
            next_agent = lock.waiters[0]
        else:
            # Default to first waiter
            next_agent = lock.waiters[0]
        
        if next_agent:
            lock.waiters.remove(next_agent)
            # Notify the next agent (would send message in real implementation)
    
    def _wait_for_lock(self, resource_id: str, deadline: float) -> bool:
        """Wait for lock acquisition or timeout"""
        while time.time() < deadline:
            with self.main_lock:
                lock = self.locks.get(resource_id)
                if lock and lock.owner_agent == self.agent_id:
                    return True
                
                # Check for deadlock
                cycle = self.deadlock_detector.detect_cycle()
                if cycle and self.agent_id in cycle:
                    deadlock_info = self.deadlock_detector.get_deadlock_info(cycle)
                    self._handle_deadlock(deadlock_info)
                    return False
            
            time.sleep(0.1)  # Short polling interval
        
        # Timeout - remove from waiters
        with self.main_lock:
            lock = self.locks.get(resource_id)
            if lock and self.agent_id in lock.waiters:
                lock.waiters.remove(self.agent_id)
                if lock.owner_agent:
                    self.deadlock_detector.remove_wait_edge(self.agent_id, lock.owner_agent)
        
        return False
    
    def _handle_deadlock(self, deadlock_info: DeadlockInfo):
        """Handle detected deadlock using resolution strategy"""
        # Broadcast deadlock detection
        message = Message(
            message_type=MessageType.DEADLOCK_DETECTED,
            from_agent=self.agent_id,
            to_agent="broadcast",
            content={
                "cycle": deadlock_info.cycle,
                "resources": deadlock_info.resources,
                "strategy": deadlock_info.resolution_strategy
            },
            priority=Priority.CRITICAL
        )
        
        self.protocol.router.send_message(message)
        
        # Apply resolution strategy (youngest dies - abort newest request)
        if deadlock_info.resolution_strategy == "youngest_dies":
            self._abort_youngest_request(deadlock_info.cycle)
    
    def _abort_youngest_request(self, cycle: List[str]):
        """Abort the youngest request in deadlock cycle"""
        # Find youngest request and abort it
        # This is a simplified implementation
        if self.agent_id in cycle:
            # Abort our own requests to break the cycle
            for resource_id, lock in self.locks.items():
                if self.agent_id in lock.waiters:
                    lock.waiters.remove(self.agent_id)
                    if lock.owner_agent:
                        self.deadlock_detector.remove_wait_edge(self.agent_id, lock.owner_agent)
    
    def _broadcast_lock_request(self, resource_id: str, priority: Priority):
        """Broadcast lock request to other agents"""
        message = Message(
            message_type=MessageType.LOCK_REQUEST,
            from_agent=self.agent_id,
            to_agent="broadcast",
            content={"resource_id": resource_id, "priority": priority.value},
            priority=priority
        )
        self.protocol.router.send_message(message)
    
    def _broadcast_lock_granted(self, resource_id: str):
        """Broadcast lock granted notification"""
        message = Message(
            message_type=MessageType.LOCK_GRANTED,
            from_agent=self.agent_id,
            to_agent="broadcast",
            content={"resource_id": resource_id},
            priority=Priority.HIGH
        )
        self.protocol.router.send_message(message)
    
    def _broadcast_lock_release(self, resource_id: str):
        """Broadcast lock release notification"""
        message = Message(
            message_type=MessageType.LOCK_RELEASED,
            from_agent=self.agent_id,
            to_agent="broadcast",
            content={"resource_id": resource_id},
            priority=Priority.NORMAL
        )
        self.protocol.router.send_message(message)
    
    def get_lock_status(self, resource_id: str) -> Dict[str, Any]:
        """Get current status of a resource lock"""
        with self.main_lock:
            lock = self.locks.get(resource_id)
            if not lock:
                return {"resource_id": resource_id, "state": "not_found"}
            
            return {
                "resource_id": resource_id,
                "state": lock.state.value,
                "owner": lock.owner_agent,
                "waiters": lock.waiters.copy(),
                "time_held": lock.time_held(),
                "is_expired": lock.is_expired(),
                "priority": lock.priority.value
            }
    
    def get_all_locks_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all resource locks"""
        with self.main_lock:
            return {rid: self.get_lock_status(rid) for rid in self.locks.keys()}
    
    def cleanup_expired_locks(self):
        """Clean up expired locks"""
        expired_locks = []
        
        with self.main_lock:
            for resource_id, lock in self.locks.items():
                if lock.is_expired() and lock.owner_agent:
                    expired_locks.append(resource_id)
        
        for resource_id in expired_locks:
            print(f"Cleaning up expired lock for resource: {resource_id}")
            self.release_lock(resource_id)


class DistributedCoordinator:
    """High-level coordinator for distributed agent collaboration"""
    
    def __init__(self, agent_id: str, communication_dir: str):
        self.agent_id = agent_id
        self.resource_coordinator = ResourceCoordinator(agent_id, communication_dir)
        self.collaboration_protocol = CollaborationProtocol(agent_id, communication_dir)
        self.active_collaborations: Dict[str, Dict] = {}
        
    def begin_collaboration(self, partner_agent: str, task_description: str, 
                          required_resources: List[str]) -> bool:
        """Begin a collaboration session with another agent"""
        # Request all required resources
        acquired_resources = []
        
        try:
            for resource in required_resources:
                if self.resource_coordinator.request_lock(resource, Priority.HIGH):
                    acquired_resources.append(resource)
                else:
                    # Failed to acquire resource - rollback
                    for acquired in acquired_resources:
                        self.resource_coordinator.release_lock(acquired)
                    return False
            
            # Send collaboration request
            success = self.collaboration_protocol.request_collaboration(
                partner_agent, task_description, {"resources": required_resources}
            )
            
            if success:
                self.active_collaborations[partner_agent] = {
                    "task": task_description,
                    "resources": required_resources,
                    "start_time": time.time(),
                    "status": "active"
                }
                return True
            else:
                # Rollback resources if collaboration request failed
                for resource in acquired_resources:
                    self.resource_coordinator.release_lock(resource)
                return False
                
        except Exception as e:
            # Rollback on any error
            for resource in acquired_resources:
                self.resource_coordinator.release_lock(resource)
            raise e
    
    def end_collaboration(self, partner_agent: str) -> bool:
        """End collaboration and release resources"""
        if partner_agent not in self.active_collaborations:
            return False
        
        collaboration = self.active_collaborations[partner_agent]
        
        # Release all resources
        for resource in collaboration["resources"]:
            self.resource_coordinator.release_lock(resource)
        
        # Update collaboration status
        collaboration["status"] = "completed"
        collaboration["end_time"] = time.time()
        
        # Send completion notification
        self.collaboration_protocol.send_status_update(
            partner_agent, "collaboration_completed", 
            {"duration": time.time() - collaboration["start_time"]}
        )
        
        return True
    
    def get_collaboration_status(self) -> Dict[str, Dict]:
        """Get status of all active collaborations"""
        return self.active_collaborations.copy()
    
    def health_check(self) -> Dict[str, Any]:
        """Perform system health check"""
        return {
            "agent_id": self.agent_id,
            "timestamp": time.time(),
            "active_collaborations": len(self.active_collaborations),
            "locks_held": len([lock for lock in self.resource_coordinator.locks.values() 
                             if lock.owner_agent == self.agent_id]),
            "deadlock_detector_active": True,
            "system_status": "healthy"
        }


# Factory function for easy instantiation
def create_synchronization_system(agent_id: str, communication_dir: str) -> DistributedCoordinator:
    """Create a complete synchronization system for an agent"""
    return DistributedCoordinator(agent_id, communication_dir)


# Example usage and testing functions
if __name__ == "__main__":
    # Example usage
    coordinator = create_synchronization_system("agent1", "/tmp/collaboration")
    
    # Test basic locking
    print("Testing resource locking...")
    success = coordinator.resource_coordinator.request_lock("shared_file.txt", Priority.HIGH)
    print(f"Lock acquired: {success}")
    
    status = coordinator.resource_coordinator.get_lock_status("shared_file.txt")
    print(f"Lock status: {status}")
    
    # Health check
    health = coordinator.health_check()
    print(f"System health: {health}")
