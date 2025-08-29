import frappe
from frappe import _
from frappe.utils import now, cint, cstr
import json
from typing import Dict, List, Any, Optional, Union


@frappe.whitelist()
def get_workflows():
    """Get all workflows that the current user has access to"""
    user = frappe.session.user
    
    # Check if the user is an administrator
    is_admin = "System Manager" in frappe.get_roles()
    
    if is_admin:
        # Admins can see all workflows
        workflows = frappe.get_all(
            "Workflow",
            fields=["name", "workflow_name", "description", "is_active", "creation", "modified", "owner", "execution_count"],
            order_by="modified desc"
        )
    else:
        # Regular users can see workflows they own or are shared with them
        workflows = frappe.get_all(
            "Workflow",
            filters=[["owner", "=", user]],
            fields=["name", "workflow_name", "description", "is_active", "creation", "modified", "owner", "execution_count"],
            order_by="modified desc"
        )
    
    result = []
    for workflow in workflows:
        # Get the nodes and edges for each workflow
        nodes = frappe.get_all(
            "Workflow Node",
            filters={"parent": workflow.name},
            fields=["*"]
        )
        
        edges = frappe.get_all(
            "Workflow Edge",
            filters={"parent": workflow.name},
            fields=["*"]
        )
        
        # Format the result to match our frontend data model
        formatted_workflow = {
            "id": workflow.name,
            "name": workflow.workflow_name,
            "description": workflow.description,
            "nodes": _format_nodes(nodes),
            "edges": _format_edges(edges),
            "metadata": {
                "createdAt": workflow.creation,
                "updatedAt": workflow.modified,
                "executionCount": workflow.execution_count or 0,
                "isActive": workflow.is_active == 1
            }
        }
        
        result.append(formatted_workflow)
    
    return result


@frappe.whitelist()
def get_workflow(workflow_id):
    """Get a specific workflow with its nodes and edges"""
    if not workflow_id:
        frappe.throw(_("Workflow ID is required"))
    
    # Check permissions
    if not _can_access_workflow(workflow_id):
        frappe.throw(_("You don't have permission to access this workflow"))
    
    # Get the workflow
    workflow = frappe.get_doc("Workflow", workflow_id)
    
    # Format the result to match our frontend data model
    formatted_workflow = {
        "id": workflow.name,
        "name": workflow.workflow_name,
        "description": workflow.description,
        "nodes": _format_nodes(workflow.nodes),
        "edges": _format_edges(workflow.edges),
        "metadata": {
            "createdAt": workflow.creation,
            "updatedAt": workflow.modified,
            "executionCount": workflow.execution_count or 0,
            "isActive": workflow.is_active == 1
        }
    }
    
    return formatted_workflow


@frappe.whitelist()
def create_workflow():
    """Create a new workflow"""
    workflow_data = json.loads(frappe.request.data)
    
    # Create a new workflow
    workflow = frappe.new_doc("Workflow")
    workflow.workflow_name = workflow_data.get("name", "New Workflow")
    workflow.description = workflow_data.get("description", "")
    workflow.is_active = 0  # Default to inactive
    workflow.execution_count = 0
    
    # If nodes and edges are provided, add them to the workflow
    if "nodes" in workflow_data:
        _add_nodes_to_workflow(workflow, workflow_data["nodes"])
    
    if "edges" in workflow_data:
        _add_edges_to_workflow(workflow, workflow_data["edges"])
    
    workflow.insert()
    
    # Return the created workflow
    return get_workflow(workflow.name)


@frappe.whitelist()
def update_workflow():
    """Update an existing workflow"""
    data = json.loads(frappe.request.data)
    workflow_id = data.get("workflow_id")
    workflow_data = data.get("workflow")
    
    if not workflow_id:
        frappe.throw(_("Workflow ID is required"))
    
    # Check permissions
    if not _can_access_workflow(workflow_id):
        frappe.throw(_("You don't have permission to update this workflow"))
    
    # Get the existing workflow
    workflow = frappe.get_doc("Workflow", workflow_id)
    
    # Update basic workflow fields
    if workflow_data.get("name"):
        workflow.workflow_name = workflow_data["name"]
    
    if "description" in workflow_data:
        workflow.description = workflow_data["description"]
    
    if "metadata" in workflow_data and "isActive" in workflow_data["metadata"]:
        workflow.is_active = 1 if workflow_data["metadata"]["isActive"] else 0
    
    # Clear existing nodes and edges
    workflow.nodes = []
    workflow.edges = []
    
    # Add updated nodes and edges
    if "nodes" in workflow_data:
        _add_nodes_to_workflow(workflow, workflow_data["nodes"])
    
    if "edges" in workflow_data:
        _add_edges_to_workflow(workflow, workflow_data["edges"])
    
    workflow.modified = now()
    workflow.save()
    
    # Return the updated workflow
    return get_workflow(workflow.name)


@frappe.whitelist()
def delete_workflow():
    """Delete a workflow"""
    data = json.loads(frappe.request.data)
    workflow_id = data.get("workflow_id")
    
    if not workflow_id:
        frappe.throw(_("Workflow ID is required"))
    
    # Check permissions
    if not _can_access_workflow(workflow_id, require_admin=True):
        frappe.throw(_("You don't have permission to delete this workflow"))
    
    # Delete the workflow
    frappe.delete_doc("Workflow", workflow_id)
    
    return {"success": True}


@frappe.whitelist()
def execute_workflow():
    """Start a workflow execution"""
    data = json.loads(frappe.request.data)
    workflow_id = data.get("workflow_id")
    input_data = data.get("input_data", {})
    
    if not workflow_id:
        frappe.throw(_("Workflow ID is required"))
    
    # Check permissions
    if not _can_access_workflow(workflow_id):
        frappe.throw(_("You don't have permission to execute this workflow"))
    
    # Create a new workflow execution
    execution = frappe.new_doc("Workflow Execution")
    execution.workflow = workflow_id
    execution.status = "Running"
    execution.start_time = now()
    execution.input_data = json.dumps(input_data)
    execution.user = frappe.session.user
    execution.insert()
    
    # Increment execution count
    workflow = frappe.get_doc("Workflow", workflow_id)
    workflow.execution_count = (workflow.execution_count or 0) + 1
    workflow.save()
    
    # Start the execution process in the background
    # In a production system, this would be a background job
    # For this example, we'll just simulate the execution
    _start_workflow_execution(execution.name)
    
    return {"execution_id": execution.name}


@frappe.whitelist()
def stop_workflow_execution():
    """Stop a workflow execution"""
    data = json.loads(frappe.request.data)
    execution_id = data.get("execution_id")
    
    if not execution_id:
        frappe.throw(_("Execution ID is required"))
    
    # Get the execution
    execution = frappe.get_doc("Workflow Execution", execution_id)
    
    # Check permissions
    if not _can_access_workflow(execution.workflow):
        frappe.throw(_("You don't have permission to stop this execution"))
    
    # Update status
    execution.status = "Stopped"
    execution.end_time = now()
    execution.save()
    
    return {"success": True}


@frappe.whitelist()
def get_execution_status(execution_id):
    """Get the status of a workflow execution"""
    if not execution_id:
        frappe.throw(_("Execution ID is required"))
    
    # Get the execution
    execution = frappe.get_doc("Workflow Execution", execution_id)
    
    # Check permissions
    if not _can_access_workflow(execution.workflow):
        frappe.throw(_("You don't have permission to access this execution"))
    
    # Get node execution statuses
    node_executions = frappe.get_all(
        "Workflow Node Execution",
        filters={"parent": execution_id},
        fields=["node_id", "status", "message", "start_time", "end_time"]
    )
    
    node_statuses = {}
    for node_exec in node_executions:
        node_statuses[node_exec.node_id] = {
            "status": node_exec.status.lower(),
            "message": node_exec.message,
            "startTime": node_exec.start_time,
            "endTime": node_exec.end_time
        }
    
    return {
        "id": execution.name,
        "workflowId": execution.workflow,
        "status": execution.status.lower(),
        "startTime": execution.start_time,
        "endTime": execution.end_time,
        "nodes": node_statuses,
        "output": json.loads(execution.output_data) if execution.output_data else {}
    }


@frappe.whitelist()
def get_node_types():
    """Get all available node types"""
    node_types = frappe.get_all(
        "Workflow Node Type",
        fields=["name", "type_name", "category", "description", "icon", "color", "inputs", "outputs", "params_schema"]
    )
    
    result = []
    for node_type in node_types:
        # Format the node type to match our frontend data model
        formatted_type = {
            "id": node_type.name,
            "type": node_type.type_name,
            "category": node_type.category,
            "description": node_type.description,
            "icon": node_type.icon,
            "color": node_type.color,
            "inputs": json.loads(node_type.inputs) if node_type.inputs else [],
            "outputs": json.loads(node_type.outputs) if node_type.outputs else [],
            "paramsSchema": json.loads(node_type.params_schema) if node_type.params_schema else {}
        }
        
        result.append(formatted_type)
    
    return result


@frappe.whitelist()
def get_workflow_templates():
    """Get all workflow templates"""
    templates = frappe.get_all(
        "Workflow Template",
        fields=["name", "template_name", "description", "category", "preview_image", "creation", "owner"]
    )
    
    result = []
    for template in templates:
        # Format the template to match our frontend data model
        formatted_template = {
            "id": template.name,
            "name": template.template_name,
            "description": template.description,
            "category": template.category,
            "previewImage": template.preview_image,
            "createdAt": template.creation,
            "owner": template.owner
        }
        
        result.append(formatted_template)
    
    return result


@frappe.whitelist()
def create_from_template():
    """Create a new workflow from a template"""
    data = json.loads(frappe.request.data)
    template_id = data.get("template_id")
    name = data.get("name")
    
    if not template_id:
        frappe.throw(_("Template ID is required"))
    
    # Get the template
    template = frappe.get_doc("Workflow Template", template_id)
    
    # Create a new workflow from the template
    workflow = frappe.new_doc("Workflow")
    workflow.workflow_name = name or template.template_name
    workflow.description = template.description
    workflow.is_active = 0  # Default to inactive
    workflow.execution_count = 0
    
    # Copy template nodes and edges
    for node in template.nodes:
        workflow.append("nodes", {
            "node_id": node.node_id,
            "node_type": node.node_type,
            "position_x": node.position_x,
            "position_y": node.position_y,
            "label": node.label,
            "parameters": node.parameters
        })
    
    for edge in template.edges:
        workflow.append("edges", {
            "edge_id": edge.edge_id,
            "source_node": edge.source_node,
            "source_handle": edge.source_handle,
            "target_node": edge.target_node,
            "target_handle": edge.target_handle,
            "label": edge.label
        })
    
    workflow.insert()
    
    # Return the created workflow
    return get_workflow(workflow.name)


# Helper functions
def _can_access_workflow(workflow_id, require_admin=False):
    """Check if the current user can access the workflow"""
    user = frappe.session.user
    
    # System managers can access all workflows
    if "System Manager" in frappe.get_roles():
        return True
    
    # If admin access is required, only system managers can proceed
    if require_admin:
        return False
    
    # Check if the user is the owner
    workflow = frappe.get_doc("Workflow", workflow_id)
    return workflow.owner == user


def _format_nodes(nodes):
    """Format workflow nodes to match frontend data model"""
    formatted_nodes = []
    for node in nodes:
        formatted_node = {
            "id": node.node_id,
            "type": "custom",  # We use a single custom node component in frontend
            "position": {
                "x": node.position_x,
                "y": node.position_y
            },
            "data": {
                "type": node.node_type,
                "label": node.label,
                "icon": node.icon,
                "color": node.color,
                "status": "idle",
                "params": json.loads(node.parameters) if node.parameters else {},
                # Add input/output sockets based on the node type
                # This would normally come from the node type definition
                "inputSockets": [],
                "outputSockets": []
            }
        }
        
        # Get node type definition to determine input/output sockets
        try:
            node_type = frappe.get_doc("Workflow Node Type", node.node_type)
            formatted_node["data"]["inputSockets"] = json.loads(node_type.inputs) if node_type.inputs else []
            formatted_node["data"]["outputSockets"] = json.loads(node_type.outputs) if node_type.outputs else []
        except:
            # If node type not found, use default sockets
            formatted_node["data"]["inputSockets"] = [{"id": "input-default", "label": "Input"}]
            formatted_node["data"]["outputSockets"] = [{"id": "output-default", "label": "Output"}]
        
        formatted_nodes.append(formatted_node)
    
    return formatted_nodes


def _format_edges(edges):
    """Format workflow edges to match frontend data model"""
    formatted_edges = []
    for edge in edges:
        formatted_edge = {
            "id": edge.edge_id,
            "source": edge.source_node,
            "sourceHandle": edge.source_handle,
            "target": edge.target_node,
            "targetHandle": edge.target_handle,
            "type": "custom",  # We use a single custom edge component in frontend
            "data": {
                "label": edge.label or ""
            }
        }
        
        formatted_edges.append(formatted_edge)
    
    return formatted_edges


def _add_nodes_to_workflow(workflow, nodes):
    """Add nodes to a workflow document"""
    for node in nodes:
        node_data = {
            "node_id": node["id"],
            "node_type": node["data"].get("type", "default"),
            "position_x": node["position"]["x"],
            "position_y": node["position"]["y"],
            "label": node["data"].get("label", ""),
            "icon": node["data"].get("icon", "📄"),
            "color": node["data"].get("color", "#3182CE"),
            "parameters": json.dumps(node["data"].get("params", {}))
        }
        workflow.append("nodes", node_data)


def _add_edges_to_workflow(workflow, edges):
    """Add edges to a workflow document"""
    for edge in edges:
        edge_data = {
            "edge_id": edge["id"],
            "source_node": edge["source"],
            "source_handle": edge.get("sourceHandle", ""),
            "target_node": edge["target"],
            "target_handle": edge.get("targetHandle", ""),
            "label": edge.get("data", {}).get("label", "")
        }
        workflow.append("edges", edge_data)


def _start_workflow_execution(execution_id):
    """Start executing a workflow (simulation)"""
    execution = frappe.get_doc("Workflow Execution", execution_id)
    workflow = frappe.get_doc("Workflow", execution.workflow)
    
    # Get start nodes (nodes with no incoming edges)
    incoming_edges = {edge.target_node for edge in workflow.edges}
    start_nodes = [node for node in workflow.nodes if node.node_id not in incoming_edges]
    
    # Create node executions for all nodes
    for node in workflow.nodes:
        # Create node execution
        node_execution = frappe.new_doc("Workflow Node Execution")
        node_execution.parent = execution_id
        node_execution.parentfield = "node_executions"
        node_execution.parenttype = "Workflow Execution"
        node_execution.node_id = node.node_id
        node_execution.status = "Pending"
        
        execution.append("node_executions", node_execution)
    
    execution.save()
    
    # In a real implementation, we would use a job queue to process the nodes
    # For simulation, we'll just mark the execution as successful after a brief delay
    import time
    
    # Mark start nodes as running
    for node in start_nodes:
        _update_node_execution_status(execution_id, node.node_id, "Running")
    
    time.sleep(1)  # Simulate processing time
    
    # Mark start nodes as completed
    for node in start_nodes:
        _update_node_execution_status(execution_id, node.node_id, "Completed")
    
    # Find next nodes in the graph and mark them
    processed_nodes = {node.node_id for node in start_nodes}
    next_nodes = _get_next_nodes(workflow, processed_nodes)
    
    # Process all remaining nodes in sequence
    while next_nodes:
        for node_id in next_nodes:
            _update_node_execution_status(execution_id, node_id, "Running")
        
        time.sleep(1)  # Simulate processing time
        
        for node_id in next_nodes:
            _update_node_execution_status(execution_id, node_id, "Completed")
        
        processed_nodes.update(next_nodes)
        next_nodes = _get_next_nodes(workflow, processed_nodes)
    
    # Mark the execution as completed
    execution = frappe.get_doc("Workflow Execution", execution_id)
    execution.status = "Completed"
    execution.end_time = now()
    execution.output_data = json.dumps({"result": "Workflow executed successfully"})
    execution.save()


def _update_node_execution_status(execution_id, node_id, status, message=None):
    """Update the status of a node execution"""
    # Find the node execution
    execution = frappe.get_doc("Workflow Execution", execution_id)
    node_execution = next((ne for ne in execution.node_executions if ne.node_id == node_id), None)
    
    if node_execution:
        node_execution.status = status
        if message:
            node_execution.message = message
        
        if status == "Running":
            node_execution.start_time = now()
        elif status in ["Completed", "Failed", "Stopped"]:
            node_execution.end_time = now()
        
        execution.save()


def _get_next_nodes(workflow, processed_nodes):
    """Get the next nodes to process based on the workflow graph"""
    next_nodes = set()
    
    for edge in workflow.edges:
        if edge.source_node in processed_nodes and edge.target_node not in processed_nodes:
            # Check if all incoming edges to this target have been processed
            all_sources_processed = True
            for other_edge in workflow.edges:
                if (other_edge.target_node == edge.target_node and
                    other_edge.source_node != edge.source_node and
                    other_edge.source_node not in processed_nodes):
                    all_sources_processed = False
                    break
            
            if all_sources_processed:
                next_nodes.add(edge.target_node)
    
    return next_nodes
