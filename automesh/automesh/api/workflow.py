import frappe
from frappe import _
from frappe.utils import now, cint, cstr
import json
from typing import Dict, List, Any, Optional, Union


@frappe.whitelist()
def get_workflows(limit=None, offset=None, search=None, tags=None, is_active=None, sort_by="modified", sort_order="desc"):
    """Get all workflows that the current user has access to with filtering and pagination"""
    user = frappe.session.user
    
    # Check if the user is an administrator
    is_admin = "System Manager" in frappe.get_roles()
    
    # Build filters
    filters = {}
    if not is_admin:
        filters["created_by"] = user
    
    if is_active is not None:
        filters["is_active"] = 1 if is_active else 0
    
    # Get workflows
    workflows = frappe.get_all(
        "Automesh Workflow",
        filters=filters,
        fields=["name", "title", "description", "is_active", "tags", "version", 
                "created_at", "updated_at", "last_executed_at", "execution_count", "created_by"],
        order_by=f"{sort_by} {sort_order}",
        limit=limit,
        start=offset
    )
    
    # Apply search filter if provided
    if search:
        search_lower = search.lower()
        workflows = [w for w in workflows if 
                    search_lower in (w.title or "").lower() or 
                    search_lower in (w.description or "").lower()]
    
    # Apply tags filter if provided
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        workflows = [w for w in workflows if w.tags and 
                    any(tag in w.tags for tag in tag_list)]
    
    result = []
    for workflow in workflows:
        # Parse workflow JSON to get nodes and edges
        workflow_json = {}
        if workflow.name:
            doc = frappe.get_doc("Automesh Workflow", workflow.name)
            if doc.workflow_json:
                try:
                    workflow_json = json.loads(doc.workflow_json)
                except:
                    workflow_json = {"nodes": [], "edges": []}
        
        # Format the result to match our frontend data model
        formatted_workflow = {
            "id": workflow.name,
            "name": workflow.title,
            "description": workflow.description or "",
            "tags": workflow.tags or "",
            "version": workflow.version or "1.0.0",
            "nodes": workflow_json.get("nodes", []),
            "edges": workflow_json.get("edges", []),
            "metadata": {
                "createdAt": workflow.created_at or workflow.get("creation"),
                "updatedAt": workflow.updated_at or workflow.get("modified"),
                "lastExecutedAt": workflow.last_executed_at,
                "executionCount": workflow.execution_count or 0,
                "isActive": workflow.is_active == 1,
                "createdBy": workflow.created_by
            }
        }
        
        result.append(formatted_workflow)
    
    # Get total count for pagination
    total = frappe.db.count("Automesh Workflow", filters)
    
    return {
        "workflows": result,
        "total": total,
        "limit": limit,
        "offset": offset
    }


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
    
    # Parse workflow JSON
    workflow_json = {"nodes": [], "edges": []}
    if workflow.workflow_json:
        try:
            workflow_json = json.loads(workflow.workflow_json)
        except:
            pass
    
    # Format the result to match our frontend data model
    formatted_workflow = {
        "id": workflow.name,
        "name": workflow.title,
        "description": workflow.description or "",
        "tags": workflow.tags or "",
        "version": workflow.version or "1.0.0",
        "nodes": workflow_json.get("nodes", []),
        "edges": workflow_json.get("edges", []),
        "metadata": {
            "createdAt": workflow.created_at or workflow.creation,
            "updatedAt": workflow.updated_at or workflow.modified,
            "lastExecutedAt": workflow.last_executed_at,
            "executionCount": workflow.execution_count or 0,
            "isActive": workflow.is_active == 1,
            "createdBy": workflow.created_by or workflow.owner
        }
    }
    
    return formatted_workflow


@frappe.whitelist()
def create_workflow():
    """Create a new workflow"""
    workflow_data = json.loads(frappe.request.data)
    
    # Create a new workflow
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = workflow_data.get("name", "New Workflow")
    workflow.description = workflow_data.get("description", "")
    workflow.version = workflow_data.get("version", "1.0.0")
    workflow.tags = workflow_data.get("tags", "")
    workflow.is_active = 0  # Default to inactive
    workflow.execution_count = 0
    workflow.created_at = now()
    workflow.updated_at = now()
    workflow.created_by = frappe.session.user
    
    # Store nodes and edges as JSON
    workflow_json = {
        "nodes": workflow_data.get("nodes", []),
        "edges": workflow_data.get("edges", [])
    }
    workflow.workflow_json = json.dumps(workflow_json)
    
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
    if workflow_data.get("name"):
        workflow.title = workflow_data["name"]
    
    if "description" in workflow_data:
        workflow.description = workflow_data["description"]
    
    if "tags" in workflow_data:
        workflow.tags = workflow_data["tags"]
    
    if "version" in workflow_data:
        workflow.version = workflow_data["version"]
    
    if "metadata" in workflow_data and "isActive" in workflow_data["metadata"]:
        workflow.is_active = 1 if workflow_data["metadata"]["isActive"] else 0
    
    # Update workflow JSON with nodes and edges
    workflow_json = {}
    if workflow.workflow_json:
        try:
            workflow_json = json.loads(workflow.workflow_json)
        except:
            workflow_json = {}
    
    if "nodes" in workflow_data:
        workflow_json["nodes"] = workflow_data["nodes"]
    
    if "edges" in workflow_data:
        workflow_json["edges"] = workflow_data["edges"]
    
    workflow.workflow_json = json.dumps(workflow_json)
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
    execution = frappe.new_doc("Workflow Execution")
    execution.workflow = workflow_id
    execution.status = "Running"
    execution.start_time = now()
    execution.input_data = json.dumps(input_data)
    execution.user = frappe.session.user
    execution.insert()
    
    # Increment execution count
    workflow = frappe.get_doc("Automesh Workflow", workflow_id)
    workflow.execution_count = (workflow.execution_count or 0) + 1
    workflow.last_executed_at = now()
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


# New Phase 1 API Endpoints

@frappe.whitelist()
def duplicate_workflow():
    """Duplicate an existing workflow"""
    data = json.loads(frappe.request.data)
    workflow_id = data.get("workflow_id")
    new_name = data.get("new_name")
    
    if not workflow_id:
        frappe.throw(_("Workflow ID is required"))
    
    # Check permissions
    if not _can_access_workflow(workflow_id):
        frappe.throw(_("You don't have permission to duplicate this workflow"))
    
    # Get original workflow
    original = frappe.get_doc("Automesh Workflow", workflow_id)
    
    # Create duplicate
    duplicate = frappe.copy_doc(original)
    duplicate.title = new_name or f"{original.title} (Copy)"
    duplicate.is_active = 0
    duplicate.execution_count = 0
    duplicate.last_executed_at = None
    duplicate.created_at = now()
    duplicate.updated_at = now()
    duplicate.created_by = frappe.session.user
    duplicate.insert()
    
    return get_workflow(duplicate.name)


@frappe.whitelist()
def toggle_workflow_status():
    """Toggle workflow active status"""
    data = json.loads(frappe.request.data)
    workflow_id = data.get("workflow_id")
    is_active = data.get("is_active")
    
    if not workflow_id:
        frappe.throw(_("Workflow ID is required"))
    
    if not _can_access_workflow(workflow_id):
        frappe.throw(_("You don't have permission to update this workflow"))
    
    workflow = frappe.get_doc("Automesh Workflow", workflow_id)
    workflow.is_active = 1 if is_active else 0
    workflow.updated_at = now()
    workflow.save()
    
    return {"success": True, "is_active": workflow.is_active}


@frappe.whitelist()
def get_workflow_statistics(days=7):
    """Get workflow statistics for dashboard"""
    user = frappe.session.user
    is_admin = "System Manager" in frappe.get_roles()
    
    # Date range
    from frappe.utils import add_days
    from_date = add_days(now(), -int(days))
    
    # Get workflows count
    workflow_filters = {}
    if not is_admin:
        workflow_filters["created_by"] = user
    
    total_workflows = frappe.db.count("Automesh Workflow", workflow_filters)
    active_workflows = frappe.db.count("Automesh Workflow", {**workflow_filters, "is_active": 1})
    
    # Get executions in date range
    exec_filters = {"start_time": [">=", from_date]}
    if not is_admin:
        # Filter by user's workflows
        user_workflows = frappe.get_all(
            "Automesh Workflow",
            filters={"created_by": user},
            pluck="name"
        )
        if user_workflows:
            exec_filters["workflow"] = ["in", user_workflows]
        else:
            # No workflows, return zeros
            return {
                "total_workflows": 0,
                "active_workflows": 0,
                "total_executions": 0,
                "completed": 0,
                "failed": 0,
                "failure_rate": "0%",
                "time_saved": "0h",
                "avg_runtime": "0s"
            }
    
    executions = frappe.get_all(
        "Automesh Execution",
        filters=exec_filters,
        fields=["status", "start_time", "end_time"]
    )
    
    total_executions = len(executions)
    completed = len([e for e in executions if e.status == "completed"])
    failed = len([e for e in executions if e.status == "failed"])
    
    # Calculate metrics
    failure_rate = (failed / total_executions * 100) if total_executions > 0 else 0
    
    # Calculate time saved (estimate: 5 min per execution)
    time_saved_minutes = completed * 5
    time_saved_hours = time_saved_minutes / 60
    
    # Calculate average runtime
    runtimes = []
    for e in executions:
        if e.start_time and e.end_time:
            runtime = (e.end_time - e.start_time).total_seconds()
            runtimes.append(runtime)
    
    avg_runtime = sum(runtimes) / len(runtimes) if runtimes else 0
    
    return {
        "total_workflows": total_workflows,
        "active_workflows": active_workflows,
        "total_executions": total_executions,
        "completed": completed,
        "failed": failed,
        "failure_rate": f"{failure_rate:.1f}%",
        "time_saved": f"{time_saved_hours:.1f}h",
        "avg_runtime": f"{avg_runtime:.1f}s"
    }


@frappe.whitelist()
def get_all_tags():
    """Get all unique tags used in workflows"""
    workflows = frappe.get_all(
        "Automesh Workflow",
        fields=["tags"]
    )
    
    all_tags = set()
    for w in workflows:
        if w.tags:
            tags = [t.strip() for t in w.tags.split(",")]
            all_tags.update(tags)
    
    return sorted(list(all_tags))


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
    workflow = frappe.get_doc("Automesh Workflow", workflow_id)
    return workflow.created_by == user or workflow.owner == user


def _start_workflow_execution(execution_id):
    """Start executing a workflow (simplified simulation for Phase 1)"""
    # Note: This is a simplified simulation for Phase 1
    # In production, this would use the workflow engine
    import time
    
    execution = frappe.get_doc("Workflow Execution", execution_id)
    
    # Simulate execution
    time.sleep(2)
    
    # Mark as completed
    execution.status = "Completed"
    execution.end_time = now()
    execution.output_data = json.dumps({"result": "Workflow executed successfully"})
    execution.save()
