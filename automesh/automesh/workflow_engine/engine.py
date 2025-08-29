import frappe
from frappe.utils import now, cint, cstr, get_datetime
import json
from datetime import datetime
import time
import traceback
from typing import Dict, List, Any, Optional, Union, Set

from .node_handlers import NodeHandlerRegistry


class ExecutionContext:
    """Context for workflow execution"""
    
    def __init__(self, execution_id):
        """Initialize execution context with execution ID"""
        self.execution_id = execution_id
        self.workflow_id = None
        self.workflow_data = {}
        self.node_outputs = {}
        self.node_branches = {}
        self.variables = {}
        self.logs = []
        self.workflow_output = None
    
    def load_execution(self):
        """Load execution data from database"""
        execution = frappe.get_doc("Automesh Execution", self.execution_id)
        self.workflow_id = execution.workflow
        
        # Load workflow
        workflow = frappe.get_doc("Automesh Workflow", self.workflow_id)
        self.workflow_data = json.loads(workflow.workflow_json) if workflow.workflow_json else {"nodes": [], "edges": []}
        
        # Load input data
        self.input_data = json.loads(execution.input_data) if execution.input_data else {}
        
        # Load workflow variables
        for var in workflow.variables:
            # Don't load secret values
            if not var.is_secret:
                # Parse complex data types
                if var.datatype == "object" or var.datatype == "array":
                    try:
                        self.variables[var.key] = json.loads(var.value)
                    except:
                        self.variables[var.key] = var.value
                elif var.datatype == "boolean":
                    self.variables[var.key] = var.value.lower() == "true"
                elif var.datatype == "number":
                    try:
                        if "." in var.value:
                            self.variables[var.key] = float(var.value)
                        else:
                            self.variables[var.key] = int(var.value)
                    except:
                        self.variables[var.key] = var.value
                else:
                    self.variables[var.key] = var.value
    
    def get_input_data(self):
        """Get the workflow input data"""
        return self.input_data
    
    def set_workflow_output(self, output):
        """Set the workflow output data"""
        self.workflow_output = output
    
    def get_node_output(self, node_id):
        """Get output data for a specific node"""
        return self.node_outputs.get(node_id, {})
    
    def set_node_output(self, node_id, output):
        """Set output data for a specific node"""
        self.node_outputs[node_id] = output
    
    def get_node_branch(self, node_id):
        """Get the branch to take for a conditional node"""
        return self.node_branches.get(node_id)
    
    def set_node_branch(self, node_id, branch):
        """Set the branch to take for a conditional node"""
        self.node_branches[node_id] = branch
    
    def get_variable(self, name, default=None):
        """Get a variable value"""
        return self.variables.get(name, default)
    
    def set_variable(self, name, value):
        """Set a variable value"""
        self.variables[name] = value
    
    def get_all_variables(self):
        """Get all variables"""
        return self.variables.copy()
    
    def get_node_by_id(self, node_id):
        """Get a node by its ID"""
        for node in self.workflow_data.get("nodes", []):
            if node.get("id") == node_id:
                return node
        return None
    
    def get_outgoing_connections(self, node_id):
        """Get all edges starting from a specific node"""
        return [
            edge for edge in self.workflow_data.get("edges", [])
            if edge.get("source") == node_id
        ]
    
    def get_incoming_connections(self, node_id):
        """Get all edges ending at a specific node"""
        return [
            edge for edge in self.workflow_data.get("edges", [])
            if edge.get("target") == node_id
        ]
    
    def log(self, node_id, level, message):
        """Add a log message"""
        self.logs.append({
            "timestamp": datetime.now().isoformat(),
            "node_id": node_id,
            "level": level,
            "message": message
        })
        
        # Create log entry in database
        frappe.db.begin()
        try:
            # We're using direct SQL to avoid the overhead of creating DocType for logs
            frappe.db.sql("""
                INSERT INTO `tabAutomesh Log` 
                (name, workflow_execution, node_id, log_level, message, creation)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                frappe.generate_hash(length=10),
                self.execution_id,
                node_id,
                level,
                message,
                now()
            ))
            frappe.db.commit()
        except Exception as e:
            frappe.db.rollback()
    
    def save_execution_status(self, status, error_message=None):
        """Save the current execution status to the database"""
        frappe.db.begin()
        try:
            execution = frappe.get_doc("Automesh Execution", self.execution_id)
            execution.status = status
            
            if status in ["completed", "failed", "cancelled"]:
                execution.end_time = now()
                
            if self.workflow_output is not None:
                execution.output_data = json.dumps(self.workflow_output)
                
            if error_message:
                execution.error_message = error_message
                
            execution.save()
            frappe.db.commit()
        except Exception as e:
            frappe.db.rollback()
            print(f"Error saving execution status: {str(e)}")
    
    def save_node_execution(self, node_id, status, error_message=None):
        """Save node execution status to the database"""
        node = self.get_node_by_id(node_id)
        if not node:
            return
            
        node_type = node.get("type", "unknown")
        
        frappe.db.begin()
        try:
            # Check if node execution record exists
            node_exec_name = f"{self.execution_id}-{node_id}"
            node_exists = frappe.db.exists("Automesh Node Execution", node_exec_name)
            
            if node_exists:
                # Update existing record
                node_exec = frappe.get_doc("Automesh Node Execution", node_exec_name)
                node_exec.status = status
                
                if status in ["completed", "failed", "cancelled"]:
                    node_exec.end_time = now()
                    
                if error_message:
                    node_exec.error_message = error_message
                    
                if status == "completed" and node_id in self.node_outputs:
                    node_exec.output_data = json.dumps(self.node_outputs.get(node_id))
                    
                node_exec.save()
            else:
                # Create new record
                node_exec = frappe.new_doc("Automesh Node Execution")
                node_exec.name = node_exec_name
                node_exec.workflow_execution = self.execution_id
                node_exec.node_id = node_id
                node_exec.node_type = node_type
                node_exec.status = status
                node_exec.start_time = now()
                
                if status in ["completed", "failed", "cancelled"]:
                    node_exec.end_time = now()
                    
                if error_message:
                    node_exec.error_message = error_message
                    
                if status == "completed" and node_id in self.node_outputs:
                    node_exec.output_data = json.dumps(self.node_outputs.get(node_id))
                    
                node_exec.insert()
                
            frappe.db.commit()
        except Exception as e:
            frappe.db.rollback()
            print(f"Error saving node execution: {str(e)}")


class WorkflowEngine:
    """Engine for executing workflows"""
    
    def __init__(self, execution_id):
        """Initialize workflow engine with execution ID"""
        self.execution_id = execution_id
        self.context = ExecutionContext(execution_id)
        
    def execute(self):
        """Execute the workflow"""
        try:
            # Load execution data
            self.context.load_execution()
            
            # Mark execution as running
            self.context.save_execution_status("running")
            
            # Find start nodes
            start_nodes = self._find_start_nodes()
            
            if not start_nodes:
                self.context.log("workflow", "ERROR", "No start nodes found in workflow")
                self.context.save_execution_status("failed", "No start nodes found in workflow")
                return False
            
            # Execute the workflow starting from start nodes
            for node_id in start_nodes:
                self._execute_node_and_successors(node_id, set())
            
            # Mark execution as completed
            self.context.save_execution_status("completed")
            return True
            
        except Exception as e:
            # Log error and mark execution as failed
            error_message = f"Workflow execution failed: {str(e)}\n{traceback.format_exc()}"
            self.context.log("workflow", "ERROR", error_message)
            self.context.save_execution_status("failed", str(e))
            return False
    
    def _find_start_nodes(self):
        """Find all start nodes in the workflow"""
        start_nodes = []
        
        for node in self.context.workflow_data.get("nodes", []):
            if node.get("type") == "start":
                start_nodes.append(node.get("id"))
        
        return start_nodes
    
    def _execute_node_and_successors(self, node_id, visited):
        """Execute a node and its successors"""
        # Check for cycles
        if node_id in visited:
            self.context.log(node_id, "WARNING", "Cycle detected in workflow")
            return
        
        # Mark node as visited
        visited.add(node_id)
        
        # Get the node
        node = self.context.get_node_by_id(node_id)
        if not node:
            self.context.log(node_id, "ERROR", f"Node {node_id} not found")
            return
        
        # Mark node as running
        self.context.save_node_execution(node_id, "running")
        
        try:
            # Execute the node
            result = self._execute_node(node)
            
            if not result.get("success"):
                # Node execution failed
                self.context.log(node_id, "ERROR", result.get("error", "Unknown error"))
                self.context.save_node_execution(node_id, "failed", result.get("error"))
                return
            
            # Mark node as completed
            self.context.save_node_execution(node_id, "completed")
            
            # Get outgoing connections
            outgoing = self.context.get_outgoing_connections(node_id)
            
            if not outgoing:
                # No outgoing connections, check if this is an end node
                if node.get("type") == "end":
                    self.context.log(node_id, "INFO", "Workflow execution reached end node")
                else:
                    self.context.log(node_id, "WARNING", "Node has no outgoing connections")
                return
            
            # Follow outgoing connections
            for edge in outgoing:
                # For conditional nodes, only follow the branch that matches the condition result
                if node.get("type") == "condition":
                    node_branch = self.context.get_node_branch(node_id)
                    edge_label = edge.get("label", "")
                    
                    if node_branch and edge_label and edge_label != node_branch:
                        # Skip this branch
                        continue
                
                # Execute the target node
                target_node_id = edge.get("target")
                self._execute_node_and_successors(target_node_id, visited.copy())
        
        except Exception as e:
            # Log error and mark node as failed
            error_message = f"Node execution failed: {str(e)}\n{traceback.format_exc()}"
            self.context.log(node_id, "ERROR", error_message)
            self.context.save_node_execution(node_id, "failed", str(e))
    
    def _execute_node(self, node):
        """Execute a single node"""
        node_id = node.get("id")
        node_type = node.get("type")
        
        # Get the appropriate handler for this node type
        handler_class = NodeHandlerRegistry.get_handler(node_type)
        
        if not handler_class:
            return {
                "success": False,
                "error": f"No handler found for node type: {node_type}"
            }
        
        try:
            # Create and execute the handler
            handler = handler_class(node, self.context)
            return handler.execute()
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing node: {str(e)}\n{traceback.format_exc()}"
            }


# Function to be called by Frappe's background job queue
def process_workflow_execution(execution, **kwargs):
    """Process a workflow execution in the background"""
    try:
        # Initialize engine
        engine = WorkflowEngine(execution)
        
        # Execute the workflow
        engine.execute()
        
    except Exception as e:
        # Log error
        print(f"Error processing workflow execution: {str(e)}\n{traceback.format_exc()}")
        
        # Update execution status
        try:
            execution_doc = frappe.get_doc("Automesh Execution", execution)
            execution_doc.status = "failed"
            execution_doc.error_message = str(e)
            execution_doc.end_time = now()
            execution_doc.save()
        except:
            pass
