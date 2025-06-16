"""
Agent Collaboration Manager
Handles discovery, handshaking, and coordination between AI agents
"""

import os
import json
import time
import re
import fcntl
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from config import ConfigManager, CollaborationConfig


@dataclass
class AgentInfo:
    """Information about an agent in the collaboration"""
    agent_id: str
    role: str
    capabilities: List[str]
    status: str
    last_seen: str
    communication_channel: str


class AgentCollaborator:
    """Main class for managing agent collaboration"""
    
    def __init__(self, agent_id: str, role: str, capabilities: List[str], config_file: str = None):
        # Validate agent_id format
        if not self._validate_agent_id(agent_id):
            raise ValueError(f"Invalid agent_id format: {agent_id}")
            
        self.agent_id = agent_id
        self.role = role
        self.capabilities = capabilities
        self.status = "INITIALIZING"
        
        # Load configuration
        self.config_manager = ConfigManager(config_file or "collaboration_config.json")
        self.config = self.config_manager.get_config()
        self.communication_dir = self.config.communication_dir
        
        self.agents: Dict[str, AgentInfo] = {}
        self.handshake_complete = False
        self.handshake_start_time: Optional[float] = None
        
    def discover_agents(self) -> List[str]:
        """Discover other agents by scanning communication directory"""
        discovered = []
        if not os.path.exists(self.communication_dir):
            os.makedirs(self.communication_dir)
            
        for filename in os.listdir(self.communication_dir):
            if filename.endswith('.txt') and 'agent' in filename.lower():
                discovered.append(filename)
                
        return discovered
    
    def announce_presence(self) -> str:
        """Announce this agent's presence and capabilities"""
        announcement = {
            "agent_id": self.agent_id,
            "role": self.role,
            "capabilities": self.capabilities,
            "status": "ACTIVE",
            "timestamp": datetime.now().isoformat(),
            "message": f"Agent {self.agent_id} is ready for collaboration"
        }
        
        filename = f"announce_{self.agent_id}_{int(time.time())}.txt"
        filepath = os.path.join(self.communication_dir, filename)
        
        content = f"AGENT ANNOUNCEMENT\n"
        content += f"==================\n"
        for key, value in announcement.items():
            content += f"{key}: {value}\n"
                
        if self._safe_file_write(filepath, content):
            self.status = "ANNOUNCED"
            self._cleanup_old_files()
            return filepath
        else:
            raise Exception(f"Failed to write announcement file: {filepath}")
    
    def initiate_handshake(self, target_agent_id: str) -> bool:
        """Initiate handshake with another agent"""
        if not self._validate_agent_id(target_agent_id):
            raise ValueError(f"Invalid target agent_id format: {target_agent_id}")
            
        self.handshake_start_time = time.time()
        
        handshake_data = {
            "from_agent": self.agent_id,
            "to_agent": target_agent_id,
            "type": "handshake_request",
            "my_role": self.role,
            "my_capabilities": self.capabilities,
            "proposed_workflow": {
                "code_writer": "agent1",
                "code_reviewer": "agent2",
                "communication_protocol": "file_based_ascii"
            },
            "timeout": self.config.handshake_timeout,
            "timestamp": datetime.now().isoformat()
        }
        
        filename = f"handshake_{self.agent_id}_to_{target_agent_id}.txt"
        filepath = os.path.join(self.communication_dir, filename)
        
        content = "HANDSHAKE REQUEST\n"
        content += "=================\n"
        for key, value in handshake_data.items():
            content += f"{key}: {value}\n"
                
        return self._safe_file_write(filepath, content)
    
    def check_for_responses(self) -> List[Dict[str, Any]]:
        """Check for responses from other agents"""
        responses = []
        
        for filename in os.listdir(self.communication_dir):
            if f"to_{self.agent_id}" in filename or f"agent2" in filename:
                filepath = os.path.join(self.communication_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                        responses.append({
                            "filename": filename,
                            "content": content,
                            "timestamp": os.path.getmtime(filepath)
                        })
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
                    
        return responses
    
    def complete_handshake(self, partner_agent_id: str) -> bool:
        """Complete handshake process with partner agent"""
        self.handshake_complete = True
        self.status = "CONNECTED"
        
        # Create handshake completion confirmation
        completion_data = {
            "from_agent": self.agent_id,
            "to_agent": partner_agent_id,
            "type": "handshake_complete",
            "status": "READY_FOR_COLLABORATION",
            "agreed_roles": {
                self.agent_id: self.role,
                partner_agent_id: "reviewer_tester"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        filename = f"handshake_complete_{self.agent_id}.txt"
        filepath = os.path.join(self.communication_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write("HANDSHAKE COMPLETE\n")
            f.write("==================\n")
            for key, value in completion_data.items():
                f.write(f"{key}: {value}\n")
                
        return True
    
    def get_collaboration_status(self) -> Dict[str, Any]:
        """Get current collaboration status"""
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "status": self.status,
            "handshake_complete": self.handshake_complete,
            "discovered_agents": len(self.agents),
            "communication_dir": self.communication_dir
        }
    
    def _validate_agent_id(self, agent_id: str) -> bool:
        """Validate agent ID format"""
        pattern = self.config.agent_id_pattern if hasattr(self, 'config') else r"^agent[1-9]\d*$"
        return bool(re.match(pattern, agent_id))
    
    def _safe_file_write(self, filepath: str, content: str) -> bool:
        """Safely write to file with locking"""
        try:
            with open(filepath, 'w') as f:
                # Use file locking for concurrent access protection
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                f.write(content)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            return True
        except Exception as e:
            print(f"Error writing file {filepath}: {e}")
            return False
    
    def _cleanup_old_files(self) -> None:
        """Clean up old communication files if limit exceeded"""
        try:
            files = [f for f in os.listdir(self.communication_dir) if f.endswith('.txt')]
            if len(files) > self.config.max_communication_files:
                # Sort by modification time and remove oldest
                files_with_time = [(f, os.path.getmtime(os.path.join(self.communication_dir, f))) 
                                 for f in files]
                files_with_time.sort(key=lambda x: x[1])
                
                files_to_remove = files_with_time[:len(files) - self.config.max_communication_files]
                for filename, _ in files_to_remove:
                    os.remove(os.path.join(self.communication_dir, filename))
        except Exception as e:
            print(f"Error cleaning up files: {e}")
    
    def _check_handshake_timeout(self) -> bool:
        """Check if handshake has timed out"""
        if self.handshake_start_time is None:
            return False
        return (time.time() - self.handshake_start_time) > self.config.handshake_timeout