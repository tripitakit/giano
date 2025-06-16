#!/usr/bin/env python3
"""
AI Agent Collaboration Framework - Complete Tutorial Suite
==========================================================

This tutorial suite provides hands-on examples for using the AI Agent
Collaboration Framework. Each tutorial builds upon previous concepts.

Prerequisites:
- Python 3.8+
- cryptography package: pip install cryptography
- Framework files: message_protocol.py, synchronization.py, workflow_engine.py

Tutorial Index:
1. Basic Agent Setup and Communication
2. Resource Coordination and Deadlock Prevention
3. Simple Workflow Creation and Execution
4. Advanced Multi-Agent Collaboration
5. Production-Ready Error Handling
6. Performance Monitoring and Optimization
"""

import os
import sys
import time
import threading
from datetime import datetime
from typing import Dict, List, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from message_protocol import (
    create_collaboration_protocol, MessageType, Priority, 
    MessageValidator, create_secure_message
)
from synchronization import (
    create_synchronization_system, CoordinationStrategy
)
from workflow_engine import (
    create_workflow_engine, ExecutionStrategy, TaskStatus, WorkflowStatus
)


class TutorialRunner:
    """Tutorial runner with setup and cleanup utilities"""
    
    def __init__(self):
        self.communication_dir = "/tmp/ai_collaboration_tutorial"
        self.setup_environment()
    
    def setup_environment(self):
        """Setup tutorial environment"""
        os.makedirs(self.communication_dir, exist_ok=True)
        print(f"Tutorial environment setup complete: {self.communication_dir}")
    
    def cleanup_environment(self):
        """Cleanup tutorial environment"""
        import shutil
        if os.path.exists(self.communication_dir):
            shutil.rmtree(self.communication_dir)
        print("Tutorial environment cleaned up")
    
    def print_section(self, title: str):
        """Print formatted section header"""
        print(f"\\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    
    def print_subsection(self, title: str):
        """Print formatted subsection header"""
        print(f"\\n{'-'*40}")
        print(f"  {title}")
        print(f"{'-'*40}")


def tutorial_1_basic_communication():
    """Tutorial 1: Basic Agent Setup and Communication"""
    tutorial = TutorialRunner()
    tutorial.print_section("Tutorial 1: Basic Agent Setup and Communication")
    
    try:
        tutorial.print_subsection("1.1 Creating Agents")
        
        # Create two agents with collaboration protocols
        agent1_protocol = create_collaboration_protocol("agent1", tutorial.communication_dir)
        agent2_protocol = create_collaboration_protocol("agent2", tutorial.communication_dir)
        
        print("✅ Created agent1 and agent2 with collaboration protocols")
        
        tutorial.print_subsection("1.2 Basic Messaging")
        
        # Agent 1 sends heartbeat to Agent 2
        print("Agent 1 sending heartbeat to Agent 2...")
        success = agent1_protocol.send_heartbeat("agent2")
        print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
        
        # Agent 1 requests collaboration
        print("\\nAgent 1 requesting collaboration with Agent 2...")
        success = agent1_protocol.request_collaboration(
            "agent2", 
            "Tutorial collaboration task",
            ["tutorial_assistance", "example_validation"]
        )
        print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
        
        tutorial.print_subsection("1.3 Message Validation and Security")
        
        # Create a secure message with encryption
        validator = MessageValidator()
        secure_msg = create_secure_message(
            "agent1", "agent2", MessageType.COLLABORATION_REQUEST,
            {"sensitive_data": "This is encrypted content"}, 
            encrypt=True
        )
        
        print(f"✅ Created secure message with ID: {secure_msg.msg_id}")
        print(f"   Encrypted: {secure_msg.content.get('encrypted', 'No')}")
        
        # Validate the message
        is_valid, error_msg = validator.validate_message(secure_msg)
        print(f"   Validation: {'✅ Valid' if is_valid else f'❌ Invalid - {error_msg}'}")
        
        tutorial.print_subsection("1.4 Message Types Demonstration")
        
        # Demonstrate different message types
        message_types = [
            (MessageType.STATUS_UPDATE, "progress", 75),
            (MessageType.TASK_DELEGATION, "delegate_task", "data_analysis"),
            (MessageType.REVIEW_REQUIRED, "code_review", "tutorial_code.py"),
            (MessageType.APPROVAL_GRANTED, "approval", "implementation_approved")
        ]
        
        for msg_type, key, value in message_types:
            msg = create_secure_message(
                "agent1", "agent2", msg_type, {key: value}
            )
            print(f"✅ Created {msg_type.value} message: {msg.content}")
        
        # Check communication directory for message files
        message_files = [f for f in os.listdir(tutorial.communication_dir) if f.endswith('.txt')]
        print(f"\\n📁 Created {len(message_files)} message files in {tutorial.communication_dir}")
        
        tutorial.print_subsection("Tutorial 1 Complete")
        print("✅ Basic communication tutorial completed successfully")
        print("🎓 Key concepts learned:")
        print("   - Agent creation and initialization")
        print("   - Basic messaging between agents")
        print("   - Message validation and security")
        print("   - Different message types and their usage")
        
    except Exception as e:
        print(f"❌ Tutorial 1 failed: {e}")
        raise
    finally:
        tutorial.cleanup_environment()


def tutorial_2_resource_coordination():
    """Tutorial 2: Resource Coordination and Deadlock Prevention"""
    tutorial = TutorialRunner()
    tutorial.print_section("Tutorial 2: Resource Coordination and Deadlock Prevention")
    
    try:
        tutorial.print_subsection("2.1 Creating Coordination Systems")
        
        # Create coordination systems for two agents
        coord1 = create_synchronization_system("agent1", tutorial.communication_dir)
        coord2 = create_synchronization_system("agent2", tutorial.communication_dir)
        
        print("✅ Created coordination systems for agent1 and agent2")
        
        tutorial.print_subsection("2.2 Basic Resource Locking")
        
        # Demonstrate basic resource acquisition
        print("Agent 1 requesting 'database' resource...")
        success = coord1.resource_coordinator.request_lock("database", Priority.HIGH, timeout=5.0)
        print(f"   Result: {'✅ Acquired' if success else '❌ Failed'}")
        
        if success:
            # Check lock status
            status = coord1.resource_coordinator.get_lock_status("database")
            print(f"   Lock status: {status}")
            
            # Release the lock
            print("\\nAgent 1 releasing 'database' resource...")
            released = coord1.resource_coordinator.release_lock("database")
            print(f"   Result: {'✅ Released' if released else '❌ Failed'}")
        
        tutorial.print_subsection("2.3 Concurrent Resource Access")
        
        results = {}
        
        def agent1_task():
            print("🤖 Agent 1: Requesting 'shared_file' resource...")
            success = coord1.resource_coordinator.request_lock("shared_file", Priority.HIGH, timeout=3.0)
            results['agent1'] = success
            if success:
                print("🤖 Agent 1: ✅ Acquired 'shared_file', working...")
                time.sleep(2)  # Simulate work
                coord1.resource_coordinator.release_lock("shared_file")
                print("🤖 Agent 1: ✅ Released 'shared_file'")
            else:
                print("🤖 Agent 1: ❌ Failed to acquire 'shared_file'")
        
        def agent2_task():
            time.sleep(0.5)  # Slight delay to create contention
            print("🤖 Agent 2: Requesting 'shared_file' resource...")
            success = coord2.resource_coordinator.request_lock("shared_file", Priority.NORMAL, timeout=5.0)
            results['agent2'] = success
            if success:
                print("🤖 Agent 2: ✅ Acquired 'shared_file', working...")
                time.sleep(1)  # Simulate work
                coord2.resource_coordinator.release_lock("shared_file")
                print("🤖 Agent 2: ✅ Released 'shared_file'")
            else:
                print("🤖 Agent 2: ❌ Failed to acquire 'shared_file'")
        
        # Run both tasks concurrently
        thread1 = threading.Thread(target=agent1_task)
        thread2 = threading.Thread(target=agent2_task)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        print(f"\\n📊 Results: Agent1: {'✅' if results.get('agent1') else '❌'}, "
              f"Agent2: {'✅' if results.get('agent2') else '❌'}")
        
        tutorial.print_subsection("2.4 Deadlock Detection Simulation")
        
        print("Simulating potential deadlock scenario...")
        
        def deadlock_agent1():
            print("🔒 Agent 1: Acquiring resource_a...")
            coord1.resource_coordinator.request_lock("resource_a", Priority.HIGH, timeout=2.0)
            time.sleep(0.5)
            print("🔒 Agent 1: Attempting to acquire resource_b...")
            success = coord1.resource_coordinator.request_lock("resource_b", Priority.HIGH, timeout=2.0)
            if not success:
                print("🔒 Agent 1: ⚠️ Deadlock detected, backing off...")
            coord1.resource_coordinator.release_lock("resource_a")
        
        def deadlock_agent2():
            time.sleep(0.1)
            print("🔒 Agent 2: Acquiring resource_b...")
            coord2.resource_coordinator.request_lock("resource_b", Priority.HIGH, timeout=2.0)
            time.sleep(0.5)
            print("🔒 Agent 2: Attempting to acquire resource_a...")
            success = coord2.resource_coordinator.request_lock("resource_a", Priority.HIGH, timeout=2.0)
            if not success:
                print("🔒 Agent 2: ⚠️ Deadlock detected, backing off...")
            coord2.resource_coordinator.release_lock("resource_b")
        
        thread1 = threading.Thread(target=deadlock_agent1)
        thread2 = threading.Thread(target=deadlock_agent2)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        tutorial.print_subsection("2.5 Health Check and Status")
        
        # Perform health checks
        health1 = coord1.health_check()
        health2 = coord2.health_check()
        
        print(f"Agent 1 health: {health1}")
        print(f"Agent 2 health: {health2}")
        
        # Check all lock statuses
        all_locks = coord1.resource_coordinator.get_all_locks_status()
        print(f"\\n📋 Current lock statuses: {all_locks}")
        
        tutorial.print_subsection("Tutorial 2 Complete")
        print("✅ Resource coordination tutorial completed successfully")
        print("🎓 Key concepts learned:")
        print("   - Resource locking and coordination")
        print("   - Priority-based resource allocation")
        print("   - Concurrent access management")
        print("   - Deadlock detection and prevention")
        print("   - System health monitoring")
        
    except Exception as e:
        print(f"❌ Tutorial 2 failed: {e}")
        raise
    finally:
        tutorial.cleanup_environment()


def tutorial_3_simple_workflow():
    """Tutorial 3: Simple Workflow Creation and Execution"""
    tutorial = TutorialRunner()
    tutorial.print_section("Tutorial 3: Simple Workflow Creation and Execution")
    
    try:
        tutorial.print_subsection("3.1 Creating Workflow Engine")
        
        # Create workflow engine
        engine = create_workflow_engine("workflow_agent", tutorial.communication_dir)
        engine.start_engine()
        print("✅ Workflow engine created and started")
        
        tutorial.print_subsection("3.2 Creating a Basic Workflow")
        
        # Create a simple data processing workflow
        workflow = engine.create_workflow(
            "Simple Data Processing",
            "Basic workflow to demonstrate task execution",
            ExecutionStrategy.SEQUENTIAL
        )
        
        print(f"✅ Created workflow: {workflow.name}")
        print(f"   ID: {workflow.workflow_id}")
        print(f"   Strategy: {workflow.execution_strategy}")
        
        tutorial.print_subsection("3.3 Adding Tasks with Dependencies")
        
        # Define task functions
        def load_data():
            print("   📥 Loading data from source...")
            time.sleep(1)
            return {"status": "loaded", "records": 1000}
        
        def validate_data():
            print("   ✅ Validating data integrity...")
            time.sleep(0.5)
            return {"status": "validated", "errors": 0}
        
        def process_data():
            print("   ⚙️ Processing data with algorithms...")
            time.sleep(1.5)
            return {"status": "processed", "output_size": "2.5MB"}
        
        def save_results():
            print("   💾 Saving results to output...")
            time.sleep(0.5)
            return {"status": "saved", "location": "/output/results.json"}
        
        # Add tasks with dependencies
        task1_id = engine.add_task_to_workflow(
            workflow, "Load Data", "Load raw data from source",
            load_data,
            required_resources=["input_source"],
            priority=Priority.HIGH
        )
        print(f"✅ Added task: Load Data (ID: {task1_id})")
        
        task2_id = engine.add_task_to_workflow(
            workflow, "Validate Data", "Validate data integrity",
            validate_data,
            dependencies=[task1_id],
            required_resources=["validator"]
        )
        print(f"✅ Added task: Validate Data (ID: {task2_id})")
        
        task3_id = engine.add_task_to_workflow(
            workflow, "Process Data", "Apply processing algorithms",
            process_data,
            dependencies=[task2_id],
            required_resources=["processor"],
            priority=Priority.HIGH
        )
        print(f"✅ Added task: Process Data (ID: {task3_id})")
        
        task4_id = engine.add_task_to_workflow(
            workflow, "Save Results", "Save processed results",
            save_results,
            dependencies=[task3_id],
            required_resources=["output_storage"]
        )
        print(f"✅ Added task: Save Results (ID: {task4_id})")
        
        print(f"\\n📊 Workflow summary: {len(workflow.tasks)} tasks created")
        
        tutorial.print_subsection("3.4 Workflow Validation")
        
        # Validate workflow for circular dependencies
        is_valid, cycles = workflow.validate_dependencies()
        if is_valid:
            print("✅ Workflow validation: PASSED")
        else:
            print(f"❌ Workflow validation: FAILED")
            print(f"   Circular dependencies: {cycles}")
            return
        
        # Display dependency graph
        dep_graph = workflow.get_dependency_graph()
        print("\\n📋 Dependency graph:")
        for task_id, deps in dep_graph.items():
            task_name = workflow.tasks[task_id].name
            dep_names = [workflow.tasks[dep].name for dep in deps] if deps else ["None"]
            print(f"   {task_name} depends on: {', '.join(dep_names)}")
        
        tutorial.print_subsection("3.5 Workflow Execution")
        
        # Submit workflow for execution
        print("Submitting workflow for execution...")
        success = engine.submit_workflow(workflow)
        if success:
            print("✅ Workflow submitted successfully")
        else:
            print("❌ Failed to submit workflow")
            return
        
        # Monitor workflow execution
        print("\\n🔄 Monitoring workflow execution:")
        start_time = time.time()
        
        while True:
            status = engine.scheduler.get_workflow_status(workflow.workflow_id)
            if status:
                elapsed = time.time() - start_time
                print(f"   [{elapsed:.1f}s] Progress: {status['progress']:.1f}% - Status: {status['status']}")
                
                if status['status'] in ['completed', 'failed', 'cancelled']:
                    break
            
            time.sleep(1)
        
        tutorial.print_subsection("3.6 Results and Analysis")
        
        # Get final status
        final_status = engine.scheduler.get_workflow_status(workflow.workflow_id)
        print(f"\\n📊 Final Workflow Report:")
        print(f"   Status: {final_status['status']}")
        print(f"   Total tasks: {final_status['total_tasks']}")
        print(f"   Completed tasks: {final_status['completed_tasks']}")
        print(f"   Progress: {final_status['progress']:.1f}%")
        print(f"   Execution strategy: {final_status['execution_strategy']}")
        
        # Display individual task results
        print("\\n📋 Task Results:")
        for task in workflow.tasks.values():
            print(f"   {task.name}: {task.status.value}")
            if task.result:
                print(f"      Result: {task.result}")
            if task.execution_time > 0:
                print(f"      Execution time: {task.execution_time:.2f}s")
        
        tutorial.print_subsection("Tutorial 3 Complete")
        print("✅ Simple workflow tutorial completed successfully")
        print("🎓 Key concepts learned:")
        print("   - Workflow engine creation and management")
        print("   - Task definition with dependencies")
        print("   - Workflow validation and execution")
        print("   - Progress monitoring and status tracking")
        print("   - Result collection and analysis")
        
        # Stop the engine
        engine.stop_engine()
        print("\\n🛑 Workflow engine stopped")
        
    except Exception as e:
        print(f"❌ Tutorial 3 failed: {e}")
        raise
    finally:
        tutorial.cleanup_environment()


def tutorial_4_multi_agent_collaboration():
    """Tutorial 4: Advanced Multi-Agent Collaboration"""
    tutorial = TutorialRunner()
    tutorial.print_section("Tutorial 4: Advanced Multi-Agent Collaboration")
    
    try:
        tutorial.print_subsection("4.1 Setting Up Multiple Agents")
        
        # Create multiple agents with different roles
        data_agent_engine = create_workflow_engine("data_agent", tutorial.communication_dir)
        analysis_agent_engine = create_workflow_engine("analysis_agent", tutorial.communication_dir)
        report_agent_engine = create_workflow_engine("report_agent", tutorial.communication_dir)
        
        # Create coordination systems
        data_coord = create_synchronization_system("data_agent", tutorial.communication_dir)
        analysis_coord = create_synchronization_system("analysis_agent", tutorial.communication_dir)
        report_coord = create_synchronization_system("report_agent", tutorial.communication_dir)
        
        # Start all engines
        data_agent_engine.start_engine()
        analysis_agent_engine.start_engine()
        report_agent_engine.start_engine()
        
        print("✅ Created and started 3 agents:")
        print("   🔵 data_agent: Data preparation specialist")
        print("   🟡 analysis_agent: Data analysis specialist")
        print("   🟢 report_agent: Report generation specialist")
        
        tutorial.print_subsection("4.2 Collaborative Workflow Design")
        
        # Results storage for cross-agent communication
        shared_results = {}
        
        def data_agent_workflow():
            """Data agent prepares data for analysis"""
            print("\\n🔵 Data Agent: Starting data preparation workflow")
            
            workflow = data_agent_engine.create_workflow(
                "Data Preparation Pipeline",
                "Prepare and validate data for analysis",
                ExecutionStrategy.SEQUENTIAL
            )
            
            def extract_data():
                print("🔵 Data Agent: Extracting data from sources...")
                time.sleep(1)
                data = {"records": 5000, "sources": ["db1", "db2", "api"]}
                shared_results["raw_data"] = data
                return data
            
            def clean_data():
                print("🔵 Data Agent: Cleaning and preprocessing data...")
                time.sleep(1.5)
                cleaned = {"records": 4800, "quality_score": 0.95}
                shared_results["cleaned_data"] = cleaned
                # Signal data is ready for analysis
                data_coord.resource_coordinator.request_lock("prepared_data", Priority.HIGH)
                return cleaned
            
            def notify_analysis_agent():
                print("🔵 Data Agent: Notifying analysis agent...")
                protocol = create_collaboration_protocol("data_agent", tutorial.communication_dir)
                protocol.request_collaboration(
                    "analysis_agent", 
                    "Analyze prepared data",
                    ["statistical_analysis", "pattern_recognition"]
                )
                return "notification_sent"
            
            # Add tasks
            task1_id = data_agent_engine.add_task_to_workflow(
                workflow, "Extract Data", "Extract raw data",
                extract_data, required_resources=["data_sources"]
            )
            
            task2_id = data_agent_engine.add_task_to_workflow(
                workflow, "Clean Data", "Clean and preprocess",
                clean_data, dependencies=[task1_id],
                required_resources=["data_processor"]
            )
            
            task3_id = data_agent_engine.add_task_to_workflow(
                workflow, "Notify Analysis", "Notify analysis agent",
                notify_analysis_agent, dependencies=[task2_id]
            )
            
            data_agent_engine.submit_workflow(workflow)
            
            # Wait for completion
            while True:
                status = data_agent_engine.scheduler.get_workflow_status(workflow.workflow_id)
                if status and status['status'] in ['completed', 'failed']:
                    break
                time.sleep(0.5)
            
            print("🔵 Data Agent: ✅ Data preparation completed")
        
        def analysis_agent_workflow():
            """Analysis agent processes prepared data"""
            time.sleep(2)  # Wait for data agent to start
            print("\\n🟡 Analysis Agent: Starting analysis workflow")
            
            workflow = analysis_agent_engine.create_workflow(
                "Data Analysis Pipeline",
                "Perform statistical analysis on prepared data",
                ExecutionStrategy.PARALLEL
            )
            
            def wait_for_data():
                print("🟡 Analysis Agent: Waiting for prepared data...")
                success = analysis_coord.resource_coordinator.request_lock(
                    "prepared_data", Priority.NORMAL, timeout=10
                )
                if success:
                    print("🟡 Analysis Agent: ✅ Received prepared data")
                    return shared_results.get("cleaned_data", {})
                else:
                    raise Exception("Prepared data not available")
            
            def statistical_analysis():
                print("🟡 Analysis Agent: Performing statistical analysis...")
                time.sleep(2)
                stats = {"mean": 42.7, "std": 8.3, "correlation": 0.75}
                shared_results["statistics"] = stats
                return stats
            
            def pattern_recognition():
                print("🟡 Analysis Agent: Running pattern recognition...")
                time.sleep(1.5)
                patterns = {"clusters": 3, "anomalies": 12, "trends": ["increasing"]}
                shared_results["patterns"] = patterns
                return patterns
            
            def prepare_analysis_results():
                print("🟡 Analysis Agent: Preparing analysis results...")
                results = {
                    "statistics": shared_results.get("statistics"),
                    "patterns": shared_results.get("patterns")
                }
                shared_results["analysis_results"] = results
                # Signal analysis is complete
                analysis_coord.resource_coordinator.request_lock("analysis_complete", Priority.HIGH)
                
                # Notify report agent
                protocol = create_collaboration_protocol("analysis_agent", tutorial.communication_dir)
                protocol.request_collaboration(
                    "report_agent",
                    "Generate final report",
                    ["report_generation", "visualization"]
                )
                return results
            
            # Add tasks
            task1_id = analysis_agent_engine.add_task_to_workflow(
                workflow, "Wait for Data", "Wait for prepared data",
                wait_for_data
            )
            
            task2_id = analysis_agent_engine.add_task_to_workflow(
                workflow, "Statistical Analysis", "Perform statistics",
                statistical_analysis, dependencies=[task1_id],
                required_resources=["stats_engine"]
            )
            
            task3_id = analysis_agent_engine.add_task_to_workflow(
                workflow, "Pattern Recognition", "Find patterns",
                pattern_recognition, dependencies=[task1_id],
                required_resources=["ml_engine"]
            )
            
            task4_id = analysis_agent_engine.add_task_to_workflow(
                workflow, "Prepare Results", "Prepare analysis results",
                prepare_analysis_results, dependencies=[task2_id, task3_id]
            )
            
            analysis_agent_engine.submit_workflow(workflow)
            
            # Wait for completion
            while True:
                status = analysis_agent_engine.scheduler.get_workflow_status(workflow.workflow_id)
                if status and status['status'] in ['completed', 'failed']:
                    break
                time.sleep(0.5)
            
            print("🟡 Analysis Agent: ✅ Analysis completed")
        
        def report_agent_workflow():
            """Report agent generates final reports"""
            time.sleep(4)  # Wait for analysis to start
            print("\\n🟢 Report Agent: Starting report generation workflow")
            
            workflow = report_agent_engine.create_workflow(
                "Report Generation Pipeline",
                "Generate comprehensive analysis reports",
                ExecutionStrategy.SEQUENTIAL
            )
            
            def wait_for_analysis():
                print("🟢 Report Agent: Waiting for analysis results...")
                success = report_coord.resource_coordinator.request_lock(
                    "analysis_complete", Priority.NORMAL, timeout=15
                )
                if success:
                    print("🟢 Report Agent: ✅ Received analysis results")
                    return shared_results.get("analysis_results", {})
                else:
                    raise Exception("Analysis results not available")
            
            def generate_summary():
                print("🟢 Report Agent: Generating executive summary...")
                time.sleep(1)
                summary = {
                    "total_records": shared_results.get("cleaned_data", {}).get("records", 0),
                    "key_findings": ["Strong correlation found", "3 distinct clusters", "Minimal anomalies"],
                    "confidence": 0.92
                }
                return summary
            
            def create_visualizations():
                print("🟢 Report Agent: Creating data visualizations...")
                time.sleep(1.5)
                visualizations = {
                    "charts": ["scatter_plot", "histogram", "correlation_matrix"],
                    "format": "PNG",
                    "resolution": "1920x1080"
                }
                return visualizations
            
            def finalize_report():
                print("🟢 Report Agent: Finalizing comprehensive report...")
                time.sleep(1)
                final_report = {
                    "title": "Comprehensive Data Analysis Report",
                    "timestamp": datetime.now().isoformat(),
                    "data_summary": shared_results.get("cleaned_data"),
                    "analysis": shared_results.get("analysis_results"),
                    "visualizations": "Generated successfully",
                    "status": "complete"
                }
                shared_results["final_report"] = final_report
                print("🟢 Report Agent: ✅ Report generation completed!")
                return final_report
            
            # Add tasks
            task1_id = report_agent_engine.add_task_to_workflow(
                workflow, "Wait for Analysis", "Wait for analysis completion",
                wait_for_analysis
            )
            
            task2_id = report_agent_engine.add_task_to_workflow(
                workflow, "Generate Summary", "Create executive summary",
                generate_summary, dependencies=[task1_id],
                required_resources=["summary_generator"]
            )
            
            task3_id = report_agent_engine.add_task_to_workflow(
                workflow, "Create Visualizations", "Generate charts and graphs",
                create_visualizations, dependencies=[task1_id],
                required_resources=["visualization_engine"]
            )
            
            task4_id = report_agent_engine.add_task_to_workflow(
                workflow, "Finalize Report", "Complete final report",
                finalize_report, dependencies=[task2_id, task3_id],
                required_resources=["report_generator"]
            )
            
            report_agent_engine.submit_workflow(workflow)
            
            # Wait for completion
            while True:
                status = report_agent_engine.scheduler.get_workflow_status(workflow.workflow_id)
                if status and status['status'] in ['completed', 'failed']:
                    break
                time.sleep(0.5)
            
            print("🟢 Report Agent: ✅ Report generation completed")
        
        tutorial.print_subsection("4.3 Executing Collaborative Workflow")
        
        print("🚀 Starting collaborative multi-agent workflow execution...")
        
        # Run all agent workflows concurrently
        data_thread = threading.Thread(target=data_agent_workflow)
        analysis_thread = threading.Thread(target=analysis_agent_workflow)
        report_thread = threading.Thread(target=report_agent_workflow)
        
        start_time = time.time()
        
        data_thread.start()
        analysis_thread.start()
        report_thread.start()
        
        # Monitor overall progress
        print("\\n📊 Monitoring collaborative workflow progress...")
        while data_thread.is_alive() or analysis_thread.is_alive() or report_thread.is_alive():
            elapsed = time.time() - start_time
            active_agents = []
            if data_thread.is_alive(): active_agents.append("🔵 Data")
            if analysis_thread.is_alive(): active_agents.append("🟡 Analysis")
            if report_thread.is_alive(): active_agents.append("🟢 Report")
            
            if active_agents:
                print(f"   [{elapsed:.1f}s] Active agents: {', '.join(active_agents)}")
            time.sleep(2)
        
        data_thread.join()
        analysis_thread.join()
        report_thread.join()
        
        total_time = time.time() - start_time
        print(f"\\n🎉 Collaborative workflow completed in {total_time:.1f} seconds!")
        
        tutorial.print_subsection("4.4 Results and Analysis")
        
        # Display final results
        print("\\n📋 Collaborative Workflow Results:")
        print("="*50)
        
        if "final_report" in shared_results:
            report = shared_results["final_report"]
            print(f"📊 {report['title']}")
            print(f"   Generated: {report['timestamp']}")
            print(f"   Data processed: {report['data_summary'].get('records', 0)} records")
            print(f"   Quality score: {shared_results.get('cleaned_data', {}).get('quality_score', 0)}")
            print(f"   Analysis findings: {len(report['analysis'].get('statistics', {})) + len(report['analysis'].get('patterns', {}))} metrics")
            print(f"   Status: {report['status'].upper()}")
        
        # Resource utilization summary
        print("\\n🔧 Resource Utilization Summary:")
        all_locks = data_coord.resource_coordinator.get_all_locks_status()
        print(f"   Total resources used: {len(all_locks)}")
        for resource, status in all_locks.items():
            print(f"   {resource}: {status['state']}")
        
        # Agent health checks
        print("\\n🏥 Agent Health Status:")
        for agent_name, coord in [("Data Agent", data_coord), ("Analysis Agent", analysis_coord), ("Report Agent", report_coord)]:
            health = coord.health_check()
            print(f"   {agent_name}: {health['system_status']}")
        
        tutorial.print_subsection("Tutorial 4 Complete")
        print("✅ Multi-agent collaboration tutorial completed successfully")
        print("🎓 Key concepts learned:")
        print("   - Multi-agent coordination and communication")
        print("   - Cross-agent resource sharing and synchronization")
        print("   - Complex workflow orchestration across agents")
        print("   - Real-time collaboration monitoring")
        print("   - Collaborative result aggregation")
        
        # Stop all engines
        data_agent_engine.stop_engine()
        analysis_agent_engine.stop_engine()
        report_agent_engine.stop_engine()
        print("\\n🛑 All workflow engines stopped")
        
    except Exception as e:
        print(f"❌ Tutorial 4 failed: {e}")
        raise
    finally:
        tutorial.cleanup_environment()


def tutorial_5_error_handling():
    """Tutorial 5: Production-Ready Error Handling"""
    tutorial = TutorialRunner()
    tutorial.print_section("Tutorial 5: Production-Ready Error Handling")
    
    try:
        tutorial.print_subsection("5.1 Setting Up Error-Prone Environment")
        
        engine = create_workflow_engine("error_demo_agent", tutorial.communication_dir)
        engine.start_engine()
        print("✅ Created workflow engine for error handling demonstration")
        
        tutorial.print_subsection("5.2 Task Failure and Retry Mechanisms")
        
        # Create workflow with tasks that may fail
        workflow = engine.create_workflow(
            "Error Handling Demo",
            "Demonstrates error handling and recovery",
            ExecutionStrategy.SEQUENTIAL
        )
        
        attempt_count = 0
        
        def unreliable_task():
            nonlocal attempt_count
            attempt_count += 1
            print(f"   🔄 Attempt {attempt_count}: Executing unreliable task...")
            
            if attempt_count < 3:  # Fail first 2 attempts
                raise Exception(f"Simulated failure on attempt {attempt_count}")
            else:
                print("   ✅ Task succeeded on attempt 3!")
                return {"status": "success", "attempts": attempt_count}
        
        def dependent_task():
            print("   ⚙️ Executing dependent task...")
            return {"status": "completed", "depends_on": "unreliable_task"}
        
        # Add tasks with retry configuration
        task1_id = engine.add_task_to_workflow(
            workflow, "Unreliable Task", "Task that fails initially",
            unreliable_task,
            required_resources=["unreliable_resource"]
        )
        
        # Configure max retries
        workflow.tasks[task1_id].max_retries = 5
        
        task2_id = engine.add_task_to_workflow(
            workflow, "Dependent Task", "Task depending on unreliable task",
            dependent_task,
            dependencies=[task1_id],
            required_resources=["reliable_resource"]
        )
        
        print(f"✅ Created workflow with retry-enabled tasks")
        print(f"   Task 1: max_retries = {workflow.tasks[task1_id].max_retries}")
        
        tutorial.print_subsection("5.3 Resource Acquisition Failures")
        
        coord = create_synchronization_system("error_demo_agent", tutorial.communication_dir)
        
        def resource_failure_task():
            print("   🔒 Attempting to acquire multiple resources...")
            
            # This will simulate resource acquisition failure
            resources = ["resource_1", "resource_2", "unavailable_resource"]
            acquired = []
            
            try:
                for resource in resources:
                    print(f"   📝 Requesting {resource}...")
                    if resource == "unavailable_resource":
                        # Simulate unavailable resource
                        raise Exception(f"Resource {resource} is unavailable")
                    
                    success = coord.resource_coordinator.request_lock(resource, Priority.HIGH, timeout=1.0)
                    if success:
                        acquired.append(resource)
                        print(f"   ✅ Acquired {resource}")
                    else:
                        raise Exception(f"Failed to acquire {resource}")
                
                return {"acquired_resources": acquired}
                
            except Exception as e:
                print(f"   ❌ Resource acquisition failed: {e}")
                # Cleanup: release any acquired resources
                for resource in acquired:
                    coord.resource_coordinator.release_lock(resource)
                    print(f"   🔄 Released {resource}")
                raise
        
        task3_id = engine.add_task_to_workflow(
            workflow, "Resource Failure Demo", "Demonstrates resource rollback",
            resource_failure_task,
            dependencies=[task2_id]
        )
        
        workflow.tasks[task3_id].max_retries = 2
        
        tutorial.print_subsection("5.4 Timeout Handling")
        
        def timeout_task():
            print("   ⏰ Starting long-running task...")
            time.sleep(10)  # This will timeout
            return {"status": "completed"}
        
        task4_id = engine.add_task_to_workflow(
            workflow, "Timeout Demo", "Task that will timeout",
            timeout_task,
            dependencies=[task2_id]  # Parallel to resource failure task
        )
        
        # Set short timeout to demonstrate timeout handling
        workflow.tasks[task4_id].timeout = 3.0
        workflow.tasks[task4_id].max_retries = 1
        
        tutorial.print_subsection("5.5 Executing Error-Prone Workflow")
        
        print("🚀 Submitting error-prone workflow...")
        
        # Validate workflow
        is_valid, cycles = workflow.validate_dependencies()
        if not is_valid:
            print(f"❌ Workflow validation failed: {cycles}")
            return
        
        success = engine.submit_workflow(workflow)
        if not success:
            print("❌ Failed to submit workflow")
            return
        
        print("✅ Workflow submitted, monitoring execution...")
        
        # Monitor execution with detailed error tracking
        start_time = time.time()
        last_status = None
        
        while True:
            status = engine.scheduler.get_workflow_status(workflow.workflow_id)
            if status:
                if status != last_status:
                    elapsed = time.time() - start_time
                    print(f"\\n   [{elapsed:.1f}s] Workflow Status: {status['status']}")
                    print(f"   Progress: {status['progress']:.1f}%")
                    print(f"   Active tasks: {status['active_tasks']}")
                    last_status = status
                
                # Show task details
                for task in workflow.tasks.values():
                    if task.status == TaskStatus.FAILED and task.error:
                        print(f"   ❌ {task.name}: {task.error} (Attempt {task.retry_count}/{task.max_retries})")
                    elif task.status == TaskStatus.RUNNING:
                        print(f"   🔄 {task.name}: Running...")
                    elif task.status == TaskStatus.COMPLETED:
                        print(f"   ✅ {task.name}: Completed in {task.execution_time:.2f}s")
                
                if status['status'] in ['completed', 'failed', 'cancelled']:
                    break
            
            time.sleep(1)
        
        tutorial.print_subsection("5.6 Error Analysis and Recovery")
        
        # Detailed error analysis
        print("\\n📋 Detailed Error Analysis:")
        print("="*40)
        
        for task in workflow.tasks.values():
            print(f"\\n🏷️  Task: {task.name}")
            print(f"   Status: {task.status.value}")
            print(f"   Retry count: {task.retry_count}/{task.max_retries}")
            
            if task.error:
                print(f"   ❌ Error: {task.error}")
            
            if task.result:
                print(f"   📊 Result: {task.result}")
            
            if task.execution_time > 0:
                print(f"   ⏱️  Execution time: {task.execution_time:.2f}s")
        
        # Resource status check
        print("\\n🔧 Resource Status After Errors:")
        all_locks = coord.resource_coordinator.get_all_locks_status()
        if all_locks:
            for resource, lock_status in all_locks.items():
                print(f"   {resource}: {lock_status['state']} (Owner: {lock_status.get('owner', 'None')})")
        else:
            print("   ✅ All resources properly released")
        
        # System health check
        health = coord.health_check()
        print(f"\\n🏥 System Health: {health['system_status']}")
        print(f"   Active collaborations: {health['active_collaborations']}")
        print(f"   Locks held: {health['locks_held']}")
        
        tutorial.print_subsection("Tutorial 5 Complete")
        print("✅ Error handling tutorial completed successfully")
        print("🎓 Key concepts learned:")
        print("   - Task retry mechanisms and configuration")
        print("   - Resource acquisition failure handling")
        print("   - Automatic resource cleanup and rollback")
        print("   - Timeout handling for long-running tasks")
        print("   - Comprehensive error monitoring and analysis")
        print("   - System health validation after errors")
        
        engine.stop_engine()
        print("\\n🛑 Workflow engine stopped")
        
    except Exception as e:
        print(f"❌ Tutorial 5 failed: {e}")
        raise
    finally:
        tutorial.cleanup_environment()


def tutorial_6_performance_monitoring():
    """Tutorial 6: Performance Monitoring and Optimization"""
    tutorial = TutorialRunner()
    tutorial.print_section("Tutorial 6: Performance Monitoring and Optimization")
    
    try:
        tutorial.print_subsection("6.1 Setting Up Performance Monitoring")
        
        # Create multiple engines for performance testing
        engines = {}
        coordinators = {}
        
        for i in range(3):
            agent_id = f"perf_agent_{i+1}"
            engines[agent_id] = create_workflow_engine(agent_id, tutorial.communication_dir)
            coordinators[agent_id] = create_synchronization_system(agent_id, tutorial.communication_dir)
            engines[agent_id].start_engine()
        
        print(f"✅ Created {len(engines)} agents for performance testing")
        
        tutorial.print_subsection("6.2 Execution Strategy Performance Comparison")
        
        strategies = [
            ExecutionStrategy.SEQUENTIAL,
            ExecutionStrategy.PARALLEL,
            ExecutionStrategy.ADAPTIVE
        ]
        
        performance_results = {}
        
        for strategy in strategies:
            print(f"\\n🚀 Testing {strategy.value} execution strategy...")
            
            agent_id = f"perf_agent_{strategies.index(strategy) + 1}"
            engine = engines[agent_id]
            
            # Create performance test workflow
            workflow = engine.create_workflow(
                f"Performance Test - {strategy.value}",
                f"Performance benchmark using {strategy.value} strategy",
                strategy
            )
            
            # Add CPU-intensive tasks
            def cpu_task(task_id: int):
                def task():
                    print(f"   🔄 CPU Task {task_id}: Computing...")
                    start = time.time()
                    # Simulate CPU work
                    total = 0
                    for i in range(1000000):
                        total += i ** 0.5
                    duration = time.time() - start
                    print(f"   ✅ CPU Task {task_id}: Completed in {duration:.2f}s")
                    return {"task_id": task_id, "duration": duration, "result": total}
                return task
            
            # Add 5 CPU tasks
            task_ids = []
            for i in range(5):
                task_id = engine.add_task_to_workflow(
                    workflow, f"CPU Task {i+1}", f"CPU-intensive task {i+1}",
                    cpu_task(i+1),
                    required_resources=[f"cpu_core_{i+1}"],
                    priority=Priority.NORMAL
                )
                task_ids.append(task_id)
            
            # Add one final aggregation task
            def aggregation_task():
                print("   📊 Aggregating results...")
                time.sleep(0.5)
                return {"status": "aggregated", "task_count": len(task_ids)}
            
            final_task_id = engine.add_task_to_workflow(
                workflow, "Aggregate Results", "Aggregate all results",
                aggregation_task,
                dependencies=task_ids,
                required_resources=["aggregator"]
            )
            
            # Execute and measure performance
            start_time = time.time()
            success = engine.submit_workflow(workflow)
            
            if success:
                # Monitor execution
                while True:
                    status = engine.scheduler.get_workflow_status(workflow.workflow_id)
                    if status and status['status'] in ['completed', 'failed']:
                        break
                    time.sleep(0.1)
                
                execution_time = time.time() - start_time
                
                # Collect performance metrics
                performance_results[strategy.value] = {
                    "execution_time": execution_time,
                    "total_tasks": len(workflow.tasks),
                    "strategy": strategy.value,
                    "success": status['status'] == 'completed'
                }
                
                print(f"   📊 {strategy.value}: {execution_time:.2f}s total execution time")
            else:
                print(f"   ❌ {strategy.value}: Failed to submit workflow")
        
        tutorial.print_subsection("6.3 Resource Contention Analysis")
        
        print("\\n🔒 Testing resource contention scenarios...")
        
        # Create concurrent workflows that compete for resources
        contention_results = {}
        
        def contention_test():
            shared_resource = "shared_database"
            
            def competing_task(agent_id: str):
                def task():
                    print(f"   🏃 {agent_id}: Requesting shared resource...")
                    coord = coordinators[agent_id]
                    start_time = time.time()
                    
                    success = coord.resource_coordinator.request_lock(
                        shared_resource, Priority.NORMAL, timeout=5.0
                    )
                    
                    if success:
                        acquisition_time = time.time() - start_time
                        print(f"   ✅ {agent_id}: Acquired resource in {acquisition_time:.2f}s")
                        
                        # Hold resource for work simulation
                        time.sleep(1.0)
                        
                        coord.resource_coordinator.release_lock(shared_resource)
                        print(f"   🔓 {agent_id}: Released resource")
                        
                        return {"acquisition_time": acquisition_time, "success": True}
                    else:
                        wait_time = time.time() - start_time
                        print(f"   ❌ {agent_id}: Failed to acquire resource after {wait_time:.2f}s")
                        return {"acquisition_time": wait_time, "success": False}
                
                return task
            
            # Create workflows for each agent
            workflows = {}
            for agent_id in engines.keys():
                workflow = engines[agent_id].create_workflow(
                    f"Contention Test - {agent_id}",
                    "Test resource contention",
                    ExecutionStrategy.SEQUENTIAL
                )
                
                task_id = engines[agent_id].add_task_to_workflow(
                    workflow, "Competing Task", "Task competing for shared resource",
                    competing_task(agent_id),
                    required_resources=[shared_resource]
                )
                
                workflows[agent_id] = workflow
            
            # Submit all workflows simultaneously
            print("   🚀 Submitting concurrent workflows...")
            start_time = time.time()
            
            for agent_id, workflow in workflows.items():
                engines[agent_id].submit_workflow(workflow)
            
            # Wait for all to complete
            while True:
                all_complete = True
                for agent_id, workflow in workflows.items():
                    status = engines[agent_id].scheduler.get_workflow_status(workflow.workflow_id)
                    if not status or status['status'] not in ['completed', 'failed']:
                        all_complete = False
                        break
                
                if all_complete:
                    break
                time.sleep(0.1)
            
            total_time = time.time() - start_time
            print(f"   📊 Resource contention test completed in {total_time:.2f}s")
            
            # Analyze results
            successful_agents = 0
            total_wait_time = 0
            
            for agent_id, workflow in workflows.items():
                for task in workflow.tasks.values():
                    if task.result and task.result.get("success"):
                        successful_agents += 1
                        total_wait_time += task.result.get("acquisition_time", 0)
            
            contention_results["total_time"] = total_time
            contention_results["successful_agents"] = successful_agents
            contention_results["avg_wait_time"] = total_wait_time / max(successful_agents, 1)
        
        contention_test()
        
        tutorial.print_subsection("6.4 System Health and Resource Monitoring")
        
        print("\\n🏥 Performing comprehensive system health checks...")
        
        # Health check for all agents
        health_summary = {}
        for agent_id, coord in coordinators.items():
            health = coord.health_check()
            health_summary[agent_id] = health
            print(f"   {agent_id}: {health['system_status']}")
        
        # Resource usage analysis
        print("\\n🔧 Resource Usage Analysis:")
        total_locks = 0
        for agent_id, coord in coordinators.items():
            locks = coord.resource_coordinator.get_all_locks_status()
            agent_locks = len([l for l in locks.values() if l.get('owner') == agent_id])
            total_locks += agent_locks
            print(f"   {agent_id}: {agent_locks} active locks")
        
        print(f"   Total system locks: {total_locks}")
        
        # Engine status summary
        print("\\n⚙️ Engine Status Summary:")
        for agent_id, engine in engines.items():
            status = engine.get_engine_status()
            print(f"   {agent_id}: {status['active_workflows']} active workflows")
        
        tutorial.print_subsection("6.5 Performance Results and Recommendations")
        
        print("\\n📊 Performance Analysis Results:")
        print("="*50)
        
        # Execution strategy comparison
        if performance_results:
            print("\\n🚀 Execution Strategy Performance:")
            sorted_results = sorted(performance_results.items(), key=lambda x: x[1]['execution_time'])
            
            for strategy, result in sorted_results:
                print(f"   {strategy}: {result['execution_time']:.2f}s")
                if result == sorted_results[0][1]:
                    print("     🏆 FASTEST")
            
            # Performance recommendations
            fastest_strategy = sorted_results[0][0]
            print(f"\\n💡 Recommendation: Use {fastest_strategy} strategy for similar workloads")
        
        # Resource contention analysis
        if contention_results:
            print("\\n🔒 Resource Contention Analysis:")
            print(f"   Total execution time: {contention_results['total_time']:.2f}s")
            print(f"   Successful acquisitions: {contention_results['successful_agents']}")
            print(f"   Average wait time: {contention_results['avg_wait_time']:.2f}s")
            
            if contention_results['avg_wait_time'] > 1.0:
                print("   ⚠️  High contention detected - consider resource pooling")
            else:
                print("   ✅ Acceptable contention levels")
        
        # System optimization recommendations
        print("\\n🎯 System Optimization Recommendations:")
        print("   - For CPU-intensive tasks: Use PARALLEL execution strategy")
        print("   - For I/O-intensive tasks: Use ADAPTIVE execution strategy")
        print("   - For sequential dependencies: Use SEQUENTIAL execution strategy")
        print("   - Monitor resource contention and adjust timeouts accordingly")
        print("   - Use resource pooling for highly contended resources")
        
        tutorial.print_subsection("Tutorial 6 Complete")
        print("✅ Performance monitoring tutorial completed successfully")
        print("🎓 Key concepts learned:")
        print("   - Execution strategy performance comparison")
        print("   - Resource contention analysis and mitigation")
        print("   - System health monitoring and metrics collection")
        print("   - Performance optimization recommendations")
        print("   - Production-ready monitoring techniques")
        
        # Stop all engines
        for engine in engines.values():
            engine.stop_engine()
        print(f"\\n🛑 All {len(engines)} workflow engines stopped")
        
    except Exception as e:
        print(f"❌ Tutorial 6 failed: {e}")
        raise
    finally:
        tutorial.cleanup_environment()


def main():
    """Main tutorial runner"""
    print("🎓 AI Agent Collaboration Framework - Tutorial Suite")
    print("="*60)
    print("Choose a tutorial to run:")
    print("1. Basic Agent Setup and Communication")
    print("2. Resource Coordination and Deadlock Prevention")
    print("3. Simple Workflow Creation and Execution")
    print("4. Advanced Multi-Agent Collaboration")
    print("5. Production-Ready Error Handling")
    print("6. Performance Monitoring and Optimization")
    print("0. Run all tutorials")
    
    try:
        choice = input("\\nEnter your choice (0-6): ").strip()
        
        tutorials = {
            "1": tutorial_1_basic_communication,
            "2": tutorial_2_resource_coordination,
            "3": tutorial_3_simple_workflow,
            "4": tutorial_4_multi_agent_collaboration,
            "5": tutorial_5_error_handling,
            "6": tutorial_6_performance_monitoring
        }
        
        if choice == "0":
            print("\\n🚀 Running all tutorials...")
            for i, tutorial_func in enumerate(tutorials.values(), 1):
                print(f"\\n\\n{'🎯'*20} TUTORIAL {i} {'🎯'*20}")
                tutorial_func()
                time.sleep(2)  # Brief pause between tutorials
        elif choice in tutorials:
            tutorials[choice]()
        else:
            print("❌ Invalid choice. Please select 0-6.")
            return
        
        print("\\n" + "🎉"*60)
        print("🎉 ALL TUTORIALS COMPLETED SUCCESSFULLY! 🎉")
        print("🎉"*60)
        print("\\n🎓 Congratulations! You have mastered the AI Agent Collaboration Framework!")
        print("\\n📚 Next steps:")
        print("   - Review the complete documentation (DOCUMENTATION.md)")
        print("   - Explore the framework source code")
        print("   - Build your own multi-agent applications")
        print("   - Contribute to the framework development")
        
    except KeyboardInterrupt:
        print("\\n\\n⚠️ Tutorial interrupted by user")
    except Exception as e:
        print(f"\\n\\n❌ Tutorial suite failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\\n👋 Thank you for using the AI Agent Collaboration Framework!")


if __name__ == "__main__":
    main()
