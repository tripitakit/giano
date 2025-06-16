"""
Configuration module for Agent Collaboration System
Handles settings and configuration management
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CollaborationConfig:
    """Configuration settings for agent collaboration"""
    communication_dir: str = "/home/patrick/projects/giano/chat"
    storage_file: str = "tasks.json"
    backup_dir: str = "backups"
    handshake_timeout: int = 300  # 5 minutes
    discovery_interval: int = 1   # 1 second
    max_communication_files: int = 100
    agent_id_pattern: str = r"^agent[1-9]\d*$"
    
    def __post_init__(self):
        """Ensure directories exist"""
        os.makedirs(self.communication_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)


class ConfigManager:
    """Manages configuration loading and saving"""
    
    def __init__(self, config_file: str = "collaboration_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> CollaborationConfig:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    return CollaborationConfig(**data)
            except Exception as e:
                print(f"Error loading config: {e}, using defaults")
        
        # Return default config and save it
        config = CollaborationConfig()
        self.save_config(config)
        return config
    
    def save_config(self, config: CollaborationConfig) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                # Convert dataclass to dict for JSON serialization
                config_dict = {
                    'communication_dir': config.communication_dir,
                    'storage_file': config.storage_file,
                    'backup_dir': config.backup_dir,
                    'handshake_timeout': config.handshake_timeout,
                    'discovery_interval': config.discovery_interval,
                    'max_communication_files': config.max_communication_files,
                    'agent_id_pattern': config.agent_id_pattern
                }
                json.dump(config_dict, f, indent=2)
                return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_config(self) -> CollaborationConfig:
        """Get current configuration"""
        return self.config
    
    def update_config(self, **kwargs) -> bool:
        """Update specific configuration values"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            return self.save_config(self.config)
        except Exception as e:
            print(f"Error updating config: {e}")
            return False
