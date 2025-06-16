#!/usr/bin/env python3
"""
Main entry point for Agent Collaboration System
This demonstrates the collaborative method between two AI agents
"""

import sys
import time
import argparse
from manager import AgentCollaborator


def main():
    """Main function to demonstrate agent collaboration"""
    parser = argparse.ArgumentParser(description='AI Agent Collaboration System')
    parser.add_argument('--agent-id', default='agent1', help='Agent identifier (default: agent1)')
    parser.add_argument('--role', default='code_writer', help='Agent role (default: code_writer)')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--timeout', type=int, default=300, help='Handshake timeout in seconds (default: 300)')
    parser.add_argument('--demo-mode', action='store_true', help='Run in demonstration mode')
    
    args = parser.parse_args()
    
    print("=== AI Agent Collaboration System ===")
    print(f"Initializing {args.agent_id} ({args.role})...")
    
    # Initialize Agent with configuration
    agent1 = AgentCollaborator(
        agent_id=args.agent_id,
        role=args.role,
        capabilities=["python_coding", "architecture_design", "implementation", "documentation"],
        config_file=args.config
    )
    
    # Update timeout if specified
    if args.timeout != 300:
        agent1.config_manager.update_config(handshake_timeout=args.timeout)
    
    print(f"Agent Status: {agent1.get_collaboration_status()}")
    
    # Discover other agents
    print("\nDiscovering other agents...")
    discovered_files = agent1.discover_agents()
    print(f"Found communication files: {discovered_files}")
    
    # Announce presence
    print("\nAnnouncing presence...")
    try:
        announcement_file = agent1.announce_presence()
        print(f"Announced at: {announcement_file}")
    except Exception as e:
        print(f"Error announcing presence: {e}")
        return False
    
    # Check for Agent 2 and initiate handshake when found
    print(f"\nWaiting for other agents (timeout: {agent1.config.handshake_timeout}s)...")
    wait_start = time.time()
    
    while time.time() - wait_start < agent1.config.handshake_timeout:
        responses = agent1.check_for_responses()
        
        if responses:
            print(f"Found {len(responses)} responses from other agents")
            
            # Look for Agent 2 announcement or response
            for response in responses:
                if "agent2" in response["filename"].lower():
                    print("Agent 2 detected! Initiating handshake...")
                    agent1.initiate_handshake("agent2")
                    
                    # Wait a bit for handshake response
                    time.sleep(2)
                    
                    # Complete handshake
                    if agent1.complete_handshake("agent2"):
                        print("Handshake completed successfully!")
                        print("Agents are now ready for collaboration")
                        return demonstrate_collaboration(agent1)
                    
        time.sleep(1)  # Check every second
    
    print("Timeout waiting for Agent 2. Proceeding with single-agent demo...")
    return demonstrate_single_agent(agent1)


def demonstrate_collaboration(agent1):
    """Demonstrate the collaborative workflow"""
    print("\n=== COLLABORATIVE WORKFLOW DEMONSTRATION ===")
    
    print("Agent 1 (Code Writer) is ready to write code")
    print("Agent 2 (Reviewer/Tester) should be ready to review and test")
    
    # Create a task for collaboration
    task_description = """
    Task: Implement a simple task management system
    - Create Task class with basic CRUD operations
    - Implement TaskStorage for persistence
    - Add validation and error handling
    """
    
    print(f"\nTask to collaborate on: {task_description}")
    
    # Agent 1 writes initial code
    print("\nAgent 1: Writing initial Task class...")
    # This would be implemented in task.py
    
    # Create communication file for Agent 2 to review
    collaboration_file = f"{agent1.communication_dir}/04_agent1_code_ready.txt"
    with open(collaboration_file, 'w') as f:
        f.write("CODE READY FOR REVIEW\n")
        f.write("=====================\n")
        f.write(f"Agent: {agent1.agent_id}\n")
        f.write(f"Task: Task management system implementation\n")
        f.write(f"Files: task.py, storage.py\n")
        f.write(f"Status: Initial implementation complete\n")
        f.write(f"Action needed: Review and test code\n")
        f.write(f"Details: {task_description}\n")
    
    print(f"Created collaboration request: {collaboration_file}")
    print("Waiting for Agent 2 to review and provide feedback...")
    
    return True


def demonstrate_single_agent(agent1):
    """Demonstrate single agent functionality if Agent 2 is not available"""
    print("\n=== SINGLE AGENT DEMONSTRATION ===")
    print("Agent 1 will demonstrate the collaboration framework")
    
    status = agent1.get_collaboration_status()
    print(f"Final Agent Status: {status}")
    
    return True


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)