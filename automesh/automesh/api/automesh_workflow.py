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
            "Automesh Workflow",
            fields=["name", "title", "description", "version", "is_active", "created_at", 
                   "updated_at", "last_executed_at", "execution_count", "created_by"],
            order_by="updated_at desc"
        )
    else:
        # Regular users can see workflows they created or are shared with them
        workflows = frappe.get_all(
            "Automesh Workflow",
            filters=[["created_by", "=", user]],
            fields=["name", "title", "description", "version", "is_active", "created_at", 
                   "updated_at", "last_executed_at", "execution_count", "created_by"],
            order_by="updated_at desc"
        )
    
    result = []
    for workflow in workflows:
        # Parse workflow JSON data
        workflow_doc = frappe.get_doc("Automesh Workflow", workflow.name)
        workflow_data = json.loads(workflow_doc.workflow_json) if workflow_doc.workflow_json else {"nodes": [], "edges": []}
        
        # Format the result to match our frontend data model
        formatted_workflow = {
            "id": workflow.name,
            "title": workflow.title,
            "description": workflow.description,
            "version": workflow.version,
            "nodes": workflow_data.get("nodes", []),
            "edges": workflow_data.get("edges", []),
            "metadata": {
                "createdAt": workflow.created_at,
                "updatedAt": workflow.updated_at,
                "lastExecutedAt": workflow.last_executed_at,
                "executionCount": workflow.execution_count or 0,
                "isActive": workflow.is_active == 1,
                "createdBy": workflow.created_by
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
    workflow = frappe.get_doc("Automesh Workflow", workflow_id)
    workflow_data = json.loads(workflow.workflow_json) if workflow.workflow_json else {"nodes": [], "edges": []}
    
    # Format the result to match our frontend data model
    formatted_workflow = {
        "id": workflow.name,
        "title": workflow.title,
        "description": workflow.description,
        "version": workflow.version,
        "nodes": workflow_data.get("nodes", []),
        "edges": workflow_data.get("edges", []),
        "metadata": {
            "createdAt": workflow.created_at,
            "updatedAt": workflow.updated_at,
            "lastExecutedAt": workflow.last_executed_at,
            "executionCount": workflow.execution_count or 0,
            "isActive": workflow.is_active == 1,
            "createdBy": workflow.created_by
        }
    }
    
    return formatted_workflow


@frappe.whitelist()
def create_workflow():
    """Create a new workflow"""
    data = json.loads(frappe.request.data)
    workflow_data = data.get("workflow", {})
    
    # Create a new workflow
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = workflow_data.get("name", workflow_data.get("title", "New Workflow"))
    workflow.description = workflow_data.get("description", "")
    workflow.version = workflow_data.get("version", "1.0.0")
    workflow.is_active = workflow_data.get("isActive", 0)
    workflow.tags = workflow_data.get("tags", "")
    workflow.execution_count = 0
    workflow.created_at = now()
    workflow.updated_at = now()
    
    # Store the entire workflow as JSON
    workflow_json = {
        "nodes": workflow_data.get("nodes", []),
        "edges": workflow_data.get("edges", [])
    }
    workflow.workflow_json = json.dumps(workflow_json)
    
    # Create variables if provided
    if "variables" in workflow_data:
        for var_key, var_value in workflow_data["variables"].items():
            var_type = "string"
            is_secret = 0
            
            # Determine variable type
            if isinstance(var_value, bool):
                var_type = "boolean"
            elif isinstance(var_value, (int, float)):
                var_type = "number"
            elif isinstance(var_value, dict):
                var_type = "object"
                var_value = json.dumps(var_value)
            elif isinstance(var_value, list):
                var_type = "array"
                var_value = json.dumps(var_value)
                
            # Check if it's a secret variable (by convention)
            if var_key.startswith("secret_") or "password" in var_key.lower() or "token" in var_key.lower() or "key" in var_key.lower():
                is_secret = 1
                
            workflow.append("variables", {
                "key": var_key,
                "value": str(var_value),
                "datatype": var_type,
                "is_secret": is_secret
            })
    
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
    workflow = frappe.get_doc("Automesh Workflow", workflow_id)
    
    # Update basic workflow fields
    if workflow_data.get("title"):
        workflow.title = workflow_data["title"]
    
    if "description" in workflow_data:
        workflow.description = workflow_data["description"]
        
    if "version" in workflow_data:
        workflow.version = workflow_data["version"]
        
    if "tags" in workflow_data:
        workflow.tags = workflow_data["tags"]
    
    if "isActive" in workflow_data:
        workflow.is_active = 1 if workflow_data["isActive"] else 0
    
    # Update workflow JSON
    if "nodes" in workflow_data or "edges" in workflow_data:
        workflow_json = json.loads(workflow.workflow_json) if workflow.workflow_json else {"nodes": [], "edges": []}
        
        if "nodes" in workflow_data:
            workflow_json["nodes"] = workflow_data["nodes"]
        
        if "edges" in workflow_data:
            workflow_json["edges"] = workflow_data["edges"]
        
        workflow.workflow_json = json.dumps(workflow_json)
    
    # Update variables if provided
    if "variables" in workflow_data:
        # Remove existing variables
        workflow.variables = []
        
        # Add updated variables
        for var_key, var_value in workflow_data["variables"].items():
            var_type = "string"
            is_secret = 0
            
            # Determine variable type
            if isinstance(var_value, bool):
                var_type = "boolean"
            elif isinstance(var_value, (int, float)):
                var_type = "number"
            elif isinstance(var_value, dict):
                var_type = "object"
                var_value = json.dumps(var_value)
            elif isinstance(var_value, list):
                var_type = "array"
                var_value = json.dumps(var_value)
                
            # Check if it's a secret variable (by convention)
            if var_key.startswith("secret_") or "password" in var_key.lower() or "token" in var_key.lower() or "key" in var_key.lower():
                is_secret = 1
                
            workflow.append("variables", {
                "key": var_key,
                "value": str(var_value),
                "datatype": var_type,
                "is_secret": is_secret
            })
    
    workflow.updated_at = now()
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
    frappe.delete_doc("Automesh Workflow", workflow_id)
    
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
    execution = frappe.new_doc("Automesh Execution")
    execution.workflow = workflow_id
    execution.status = "queued"
    execution.start_time = now()
    
    if input_data:
        execution.input_data = json.dumps(input_data)
    
    execution.insert()
    
    # Increment execution count and update last executed timestamp
    workflow = frappe.get_doc("Automesh Workflow", workflow_id)
    workflow.execution_count = (workflow.execution_count or 0) + 1
    workflow.last_executed_at = now()
    workflow.save()
    
    # Start the execution process in the background
    frappe.enqueue(
        "automesh.automesh.workflow_engine.engine.process_workflow_execution", 
        execution=execution.name, 
        timeout=1800
    )
    
    return {"execution_id": execution.name}


@frappe.whitelist()
def stop_workflow_execution():
    """Stop a workflow execution"""
    data = json.loads(frappe.request.data)
    execution_id = data.get("execution_id")
    
    if not execution_id:
        frappe.throw(_("Execution ID is required"))
    
    # Get the execution
    execution = frappe.get_doc("Automesh Execution", execution_id)
    
    # Check permissions
    if not _can_access_workflow(execution.workflow):
        frappe.throw(_("You don't have permission to stop this execution"))
    
    # Update status
    execution.status = "cancelled"
    execution.end_time = now()
    execution.save()
    
    return {"success": True}


@frappe.whitelist()
def get_execution_status(execution_id):
    """Get the status of a workflow execution"""
    if not execution_id:
        frappe.throw(_("Execution ID is required"))
    
    # Get the execution
    execution = frappe.get_doc("Automesh Execution", execution_id)
    
    # Check permissions
    if not _can_access_workflow(execution.workflow):
        frappe.throw(_("You don't have permission to access this execution"))
    
    # Get node executions
    node_executions = frappe.get_all(
        "Automesh Node Execution",
        filters={"workflow_execution": execution_id},
        fields=["node_id", "node_type", "status", "start_time", "end_time", "error_message"]
    )
    
    node_statuses = {}
    for node_exec in node_executions:
        node_statuses[node_exec.node_id] = {
            "nodeType": node_exec.node_type,
            "status": node_exec.status.lower(),
            "errorMessage": node_exec.error_message,
            "startTime": node_exec.start_time,
            "endTime": node_exec.end_time
        }
    
    # Parse input/output data
    input_data = json.loads(execution.input_data) if execution.input_data else {}
    output_data = json.loads(execution.output_data) if execution.output_data else {}
    
    return {
        "id": execution.name,
        "workflowId": execution.workflow,
        "status": execution.status.lower(),
        "startTime": execution.start_time,
        "endTime": execution.end_time,
        "nodes": node_statuses,
        "inputData": input_data,
        "outputData": output_data
    }


@frappe.whitelist()
def get_node_types():
    """Get all available node types"""
    node_types = frappe.get_all(
        "Automesh Node Type",
        fields=["name", "type", "label", "description", "icon", "color", "category", 
                "inputs", "outputs", "is_system", "is_enabled"]
    )
    
    result = []
    for node_type in node_types:
        # Only include enabled node types
        if not node_type.is_enabled:
            continue
            
        # Parse inputs and outputs
        inputs = json.loads(node_type.inputs) if node_type.inputs else []
        outputs = json.loads(node_type.outputs) if node_type.outputs else []
        
        # Format the node type to match our frontend data model
        formatted_type = {
            "id": node_type.name,
            "type": node_type.type,
            "label": node_type.label,
            "category": node_type.category,
            "description": node_type.description,
            "icon": node_type.icon,
            "color": node_type.color,
            "inputs": inputs,
            "outputs": outputs,
            "isSystem": node_type.is_system == 1
        }
        
        result.append(formatted_type)
    
    return result


@frappe.whitelist()
def get_templates():
    """Get all workflow templates"""
    templates = frappe.get_all(
        "Automesh Template",
        fields=["name", "title", "description", "category", "tags", 
                "version", "is_featured", "created_by"]
    )
    
    result = []
    for template in templates:
        # Get template JSON data
        template_doc = frappe.get_doc("Automesh Template", template.name)
        template_data = json.loads(template_doc.template_json) if template_doc.template_json else {}
        
        # Format the template to match our frontend data model
        formatted_template = {
            "id": template.name,
            "title": template.title,
            "description": template.description,
            "category": template.category,
            "tags": template.tags,
            "version": template.version,
            "isFeatured": template.is_featured == 1,
            "createdBy": template.created_by,
            "nodes": template_data.get("nodes", []),
            "edges": template_data.get("edges", []),
            "variables": template_data.get("variables", {})
        }
        
        result.append(formatted_template)
    
    return result


@frappe.whitelist()
def create_from_template():
    """Create a new workflow from a template"""
    data = json.loads(frappe.request.data)
    template_id = data.get("template_id")
    title = data.get("title")
    
    if not template_id:
        frappe.throw(_("Template ID is required"))
    
    # Get the template
    template = frappe.get_doc("Automesh Template", template_id)
    template_data = json.loads(template.template_json) if template.template_json else {}
    
    # Create a new workflow from the template
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = title or template.title
    workflow.description = template.description
    workflow.version = "1.0.0"
    workflow.is_active = 0  # Default to inactive
    workflow.tags = template.tags
    workflow.execution_count = 0
    workflow.created_at = now()
    workflow.updated_at = now()
    
    # Store the workflow JSON data
    workflow.workflow_json = json.dumps({
        "nodes": template_data.get("nodes", []),
        "edges": template_data.get("edges", [])
    })
    
    # Add variables if present in template
    if "variables" in template_data:
        for var_key, var_value in template_data["variables"].items():
            var_type = "string"
            is_secret = 0
            
            # Determine variable type
            if isinstance(var_value, bool):
                var_type = "boolean"
            elif isinstance(var_value, (int, float)):
                var_type = "number"
            elif isinstance(var_value, dict):
                var_type = "object"
                var_value = json.dumps(var_value)
            elif isinstance(var_value, list):
                var_type = "array"
                var_value = json.dumps(var_value)
                
            # Check if it's a secret variable (by convention)
            if var_key.startswith("secret_") or "password" in var_key.lower() or "token" in var_key.lower() or "key" in var_key.lower():
                is_secret = 1
                
            workflow.append("variables", {
                "key": var_key,
                "value": str(var_value),
                "datatype": var_type,
                "is_secret": is_secret
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
    
    # Check if the user is the creator
    workflow = frappe.get_doc("Automesh Workflow", workflow_id)
    if workflow.created_by == user:
        return True
        
    # TODO: Add logic for shared workflows when implemented
    
    return False
