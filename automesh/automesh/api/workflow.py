import frappe
from frappe import _
from frappe.utils import now, cint, cstr
import json
from typing import Dict, List, Any, Optional, Union


@frappe.whitelist()
def get_workflows(limit=None, offset=None, search=None, tags=None, is_active=None, sort_by="modified", sort_order="desc"):
    """Get all workflows that the current user has access to with filtering and pagination
    
    Performance optimizations:
    - Uses SQL LIKE for search instead of Python filtering
    - Applies filters at database level
    - Batch loads workflow_json only when needed
    - Caches user role check
    """
    user = frappe.session.user
    
    # Check if the user is an administrator (cached)
    is_admin = "System Manager" in frappe.get_roles()
    
    # Build base filters
    filters = {}
    if not is_admin:
        filters["created_by"] = user
    
    if is_active is not None:
        filters["is_active"] = 1 if is_active else 0
    
    # Build SQL conditions for better performance
    conditions = []
    values = {}
    
    # Add search condition at SQL level
    if search:
        conditions.append("(title LIKE %(search)s OR description LIKE %(search)s)")
        values["search"] = f"%{search}%"
    
    # Add tags condition at SQL level
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        tag_conditions = [f"tags LIKE %(tag_{i})s" for i in range(len(tag_list))]
        conditions.append(f"({' OR '.join(tag_conditions)})")
        for i, tag in enumerate(tag_list):
            values[f"tag_{i}"] = f"%{tag}%"
    
    # Combine filters and conditions
    filter_str = " AND ".join([f"{k}=%(filter_{k})s" for k in filters.keys()])
    for k, v in filters.items():
        values[f"filter_{k}"] = v
    
    if conditions:
        if filter_str:
            filter_str += " AND " + " AND ".join(conditions)
        else:
            filter_str = " AND ".join(conditions)
    
    # Get total count first (without limit/offset)
    count_query = f"SELECT COUNT(*) as count FROM `tabAutomesh Workflow`"
    if filter_str:
        count_query += f" WHERE {filter_str}"
    
    total = frappe.db.sql(count_query, values, as_dict=True)[0].count if filter_str else frappe.db.count("Automesh Workflow")
    
    # Get workflows with optimized query
    query = f"""
        SELECT 
            name, title, description, is_active, tags, version,
            created_at, updated_at, last_executed_at, execution_count, created_by,
            workflow_json
        FROM `tabAutomesh Workflow`
    """
    
    if filter_str:
        query += f" WHERE {filter_str}"
    
    query += f" ORDER BY {sort_by} {sort_order}"
    
    if limit:
        query += f" LIMIT {int(limit)}"
    if offset:
        query += f" OFFSET {int(offset)}"
    
    workflows = frappe.db.sql(query, values, as_dict=True)
    
    # Format results
    result = []
    for workflow in workflows:
        # Parse workflow JSON (already loaded in single query)
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
                "createdAt": workflow.created_at,
                "updatedAt": workflow.updated_at,
                "lastExecutedAt": workflow.last_executed_at,
                "executionCount": workflow.execution_count or 0,
                "isActive": workflow.is_active == 1,
                "createdBy": workflow.created_by
            }
        }
        
        result.append(formatted_workflow)
    
    return {
        "workflows": result,
        "total": total,
        "limit": int(limit) if limit else None,
        "offset": int(offset) if offset else None
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
    data = json.loads(frappe.request.data)
    workflow_data = data.get("workflow", {})
    
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
    """Get workflow statistics for dashboard
    
    Performance optimizations:
    - Uses aggregation queries instead of loading all records
    - Single query for execution stats
    - Cached for 5 minutes
    """
    user = frappe.session.user
    is_admin = "System Manager" in frappe.get_roles()
    
    # Check cache first (5 minute TTL)
    cache_key = f"workflow_stats_{user}_{days}"
    cached_stats = frappe.cache().get_value(cache_key)
    if cached_stats:
        return cached_stats
    
    # Date range
    from frappe.utils import add_days
    from_date = add_days(now(), -int(days))
    
    # Get workflows count
    workflow_filters = {}
    if not is_admin:
        workflow_filters["created_by"] = user
    
    total_workflows = frappe.db.count("Automesh Workflow", workflow_filters)
    active_workflows = frappe.db.count("Automesh Workflow", {**workflow_filters, "is_active": 1})
    
    # Build execution query with aggregation
    if not is_admin:
        # Get user's workflow IDs
        user_workflows = frappe.get_all(
            "Automesh Workflow",
            filters={"created_by": user},
            pluck="name"
        )
        if not user_workflows:
            # No workflows, return zeros
            stats = {
                "total_workflows": 0,
                "active_workflows": 0,
                "total_executions": 0,
                "completed": 0,
                "failed": 0,
                "failure_rate": "0%",
                "time_saved": "0h",
                "avg_runtime": "0s"
            }
            frappe.cache().set_value(cache_key, stats, expires_in_sec=300)
            return stats
        
        workflow_condition = f"AND workflow IN ({','.join(['%s'] * len(user_workflows))})"
        workflow_values = user_workflows
    else:
        workflow_condition = ""
        workflow_values = []
    
    # Single aggregation query for all execution stats
    query = f"""
        SELECT 
            COUNT(*) as total_executions,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
            AVG(CASE 
                WHEN start_time IS NOT NULL AND end_time IS NOT NULL 
                THEN TIMESTAMPDIFF(SECOND, start_time, end_time)
                ELSE NULL 
            END) as avg_runtime
        FROM `tabAutomesh Execution`
        WHERE start_time >= %s {workflow_condition}
    """
    
    values = [from_date] + workflow_values
    result = frappe.db.sql(query, values, as_dict=True)[0]
    
    total_executions = result.total_executions or 0
    completed = result.completed or 0
    failed = result.failed or 0
    avg_runtime = result.avg_runtime or 0
    
    # Calculate metrics
    failure_rate = (failed / total_executions * 100) if total_executions > 0 else 0
    
    # Calculate time saved (estimate: 5 min per execution)
    time_saved_minutes = completed * 5
    time_saved_hours = time_saved_minutes / 60
    
    stats = {
        "total_workflows": total_workflows,
        "active_workflows": active_workflows,
        "total_executions": total_executions,
        "completed": completed,
        "failed": failed,
        "failure_rate": f"{failure_rate:.1f}%",
        "time_saved": f"{time_saved_hours:.1f}h",
        "avg_runtime": f"{avg_runtime:.1f}s"
    }
    
    # Cache for 5 minutes
    frappe.cache().set_value(cache_key, stats, expires_in_sec=300)
    
    return stats


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


# Phase 2 API Endpoints

@frappe.whitelist()
def bulk_delete_workflows():
    """Delete multiple workflows at once"""
    data = json.loads(frappe.request.data)
    workflow_ids = data.get("workflow_ids", [])
    
    if not workflow_ids:
        frappe.throw(_("Workflow IDs are required"))
    
    deleted = []
    failed = []
    
    for workflow_id in workflow_ids:
        try:
            # Check permissions
            if not _can_access_workflow(workflow_id, require_admin=True):
                failed.append({"id": workflow_id, "error": "Permission denied"})
                continue
            
            # Delete the workflow
            frappe.delete_doc("Automesh Workflow", workflow_id)
            deleted.append(workflow_id)
        except Exception as e:
            failed.append({"id": workflow_id, "error": str(e)})
    
    return {
        "success": True,
        "deleted": deleted,
        "failed": failed,
        "deleted_count": len(deleted),
        "failed_count": len(failed)
    }


@frappe.whitelist()
def bulk_update_status():
    """Update status for multiple workflows at once"""
    data = json.loads(frappe.request.data)
    workflow_ids = data.get("workflow_ids", [])
    is_active = data.get("is_active")
    
    if not workflow_ids:
        frappe.throw(_("Workflow IDs are required"))
    
    if is_active is None:
        frappe.throw(_("is_active parameter is required"))
    
    updated = []
    failed = []
    
    for workflow_id in workflow_ids:
        try:
            # Check permissions
            if not _can_access_workflow(workflow_id):
                failed.append({"id": workflow_id, "error": "Permission denied"})
                continue
            
            # Update status
            workflow = frappe.get_doc("Automesh Workflow", workflow_id)
            workflow.is_active = 1 if is_active else 0
            workflow.updated_at = now()
            workflow.save()
            updated.append(workflow_id)
        except Exception as e:
            failed.append({"id": workflow_id, "error": str(e)})
    
    return {
        "success": True,
        "updated": updated,
        "failed": failed,
        "updated_count": len(updated),
        "failed_count": len(failed)
    }


@frappe.whitelist()
def get_workflow_executions(workflow_id, limit=10, offset=0, status=None):
    """Get execution history for a workflow"""
    if not workflow_id:
        frappe.throw(_("Workflow ID is required"))
    
    if not _can_access_workflow(workflow_id):
        frappe.throw(_("You don't have permission to access this workflow"))
    
    filters = {"workflow": workflow_id}
    if status:
        filters["status"] = status
    
    executions = frappe.get_all(
        "Automesh Execution",
        filters=filters,
        fields=["name", "status", "start_time", "end_time", "created_by"],
        order_by="start_time desc",
        limit=int(limit),
        start=int(offset)
    )
    
    total = frappe.db.count("Automesh Execution", filters)
    
    return {
        "executions": executions,
        "total": total,
        "limit": int(limit),
        "offset": int(offset)
    }


@frappe.whitelist()
def get_templates(category=None):
    """Get available workflow templates"""
    filters = {}
    if category:
        filters["category"] = category
    
    templates = frappe.get_all(
        "Automesh Template",
        filters=filters,
        fields=["name", "title", "description", "category", "tags", "version", "is_featured"]
    )
    
    return templates


@frappe.whitelist()
def create_workflow_from_template():
    """Create a workflow from a template"""
    data = json.loads(frappe.request.data)
    template_id = data.get("template_id")
    workflow_name = data.get("workflow_name")
    
    if not template_id:
        frappe.throw(_("Template ID is required"))
    
    template = frappe.get_doc("Automesh Template", template_id)
    template_data = json.loads(template.template_json) if template.template_json else {}
    
    # Create workflow from template
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = workflow_name or f"{template.title} - {now()}"
    workflow.description = template.description
    workflow.workflow_json = template.template_json
    workflow.tags = template.tags
    workflow.version = "1.0.0"
    workflow.is_active = 0
    workflow.execution_count = 0
    workflow.created_at = now()
    workflow.updated_at = now()
    workflow.created_by = frappe.session.user
    workflow.insert()
    
    return get_workflow(workflow.name)


@frappe.whitelist()
def export_workflow_json():
    """Export workflow as JSON"""
    data = json.loads(frappe.request.data)
    workflow_id = data.get("workflow_id")
    
    if not workflow_id:
        frappe.throw(_("Workflow ID is required"))
    
    if not _can_access_workflow(workflow_id):
        frappe.throw(_("You don't have permission to export this workflow"))
    
    workflow = frappe.get_doc("Automesh Workflow", workflow_id)
    
    export_data = {
        "title": workflow.title,
        "description": workflow.description,
        "version": workflow.version,
        "tags": workflow.tags,
        "workflow_json": workflow.workflow_json,
        "exported_at": now(),
        "exported_by": frappe.session.user
    }
    
    return export_data


@frappe.whitelist()
def import_workflow_json():
    """Import workflow from JSON"""
    data = json.loads(frappe.request.data)
    import_data = data.get("import_data")
    
    if not import_data:
        frappe.throw(_("Import data is required"))
    
    # Validate required fields
    if not import_data.get("title") or not import_data.get("workflow_json"):
        frappe.throw(_("Invalid workflow data"))
    
    # Create workflow
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = f"{import_data['title']} (Imported)"
    workflow.description = import_data.get("description", "")
    workflow.workflow_json = import_data["workflow_json"]
    workflow.tags = import_data.get("tags", "")
    workflow.version = import_data.get("version", "1.0.0")
    workflow.is_active = 0
    workflow.execution_count = 0
    workflow.created_at = now()
    workflow.updated_at = now()
    workflow.created_by = frappe.session.user
    workflow.insert()
    
    return get_workflow(workflow.name)


@frappe.whitelist()
def share_workflow():
    """Share workflow with another user"""
    data = json.loads(frappe.request.data)
    workflow_id = data.get("workflow_id")
    shared_with = data.get("shared_with")
    permission_level = data.get("permission_level", "view")
    expires_at = data.get("expires_at")
    
    if not workflow_id or not shared_with:
        frappe.throw(_("Workflow ID and user are required"))
    
    # Only owner or admin can share
    if not _can_access_workflow(workflow_id, require_admin=True):
        frappe.throw(_("You don't have permission to share this workflow"))
    
    # Check if already shared
    existing = frappe.db.exists(
        "Automesh Workflow Share",
        {"workflow": workflow_id, "shared_with": shared_with}
    )
    
    if existing:
        # Update existing share
        share = frappe.get_doc("Automesh Workflow Share", existing)
        share.permission_level = permission_level
        share.expires_at = expires_at
        share.is_active = 1
        share.save()
    else:
        # Create new share
        share = frappe.new_doc("Automesh Workflow Share")
        share.workflow = workflow_id
        share.shared_with = shared_with
        share.permission_level = permission_level
        share.shared_by = frappe.session.user
        share.shared_at = now()
        share.expires_at = expires_at
        share.is_active = 1
        share.insert()
    
    return {"success": True, "share_id": share.name}


@frappe.whitelist()
def get_workflow_shares(workflow_id):
    """Get all shares for a workflow"""
    if not workflow_id:
        frappe.throw(_("Workflow ID is required"))
    
    # Check permissions
    if not _can_access_workflow(workflow_id):
        frappe.throw(_("You don't have permission to access this workflow"))
    
    shares = frappe.get_all(
        "Automesh Workflow Share",
        filters={"workflow": workflow_id, "is_active": 1},
        fields=["name", "shared_with", "permission_level", "shared_by", "shared_at", "expires_at"],
        order_by="shared_at desc"
    )
    
    return shares


@frappe.whitelist()
def revoke_workflow_share():
    """Revoke a workflow share"""
    data = json.loads(frappe.request.data)
    share_id = data.get("share_id")
    
    if not share_id:
        frappe.throw(_("Share ID is required"))
    
    share = frappe.get_doc("Automesh Workflow Share", share_id)
    
    # Check permissions - only owner or admin can revoke
    if not _can_access_workflow(share.workflow, require_admin=True):
        frappe.throw(_("You don't have permission to revoke this share"))
    
    # Deactivate the share
    share.is_active = 0
    share.save()
    
    return {"success": True}


@frappe.whitelist()
def update_workflow_share():
    """Update a workflow share's permission level"""
    data = json.loads(frappe.request.data)
    share_id = data.get("share_id")
    permission_level = data.get("permission_level")
    
    if not share_id or not permission_level:
        frappe.throw(_("Share ID and permission level are required"))
    
    share = frappe.get_doc("Automesh Workflow Share", share_id)
    
    # Check permissions
    if not _can_access_workflow(share.workflow, require_admin=True):
        frappe.throw(_("You don't have permission to update this share"))
    
    share.permission_level = permission_level
    share.save()
    
    return {"success": True}


# Helper functions
def _can_access_workflow(workflow_id, require_admin=False):
    """Check if the current user can access the workflow"""
    user = frappe.session.user
    
    # System managers can access all workflows
    if "System Manager" in frappe.get_roles():
        return True
    
    # Check if the user is the owner
    workflow = frappe.get_doc("Automesh Workflow", workflow_id)
    is_owner = workflow.created_by == user or workflow.owner == user
    
    if is_owner:
        return True
    
    # If admin access is required, check for 'full' permission level
    if require_admin:
        shares = frappe.get_all(
            "Automesh Workflow Share",
            filters={
                "workflow": workflow_id,
                "shared_with": user,
                "is_active": 1,
                "permission_level": "full"
            }
        )
        return len(shares) > 0
    
    # Check if shared with user (any permission level)
    shares = frappe.get_all(
        "Automesh Workflow Share",
        filters={
            "workflow": workflow_id,
            "shared_with": user,
            "is_active": 1
        },
        fields=["permission_level", "expires_at"]
    )
    
    if shares:
        # Check if any share is still valid (not expired)
        for share in shares:
            if not share.expires_at or share.expires_at > now():
                return True
    
    return False


def _get_user_permission_level(workflow_id, user=None):
    """Get the user's permission level for a workflow"""
    if not user:
        user = frappe.session.user
    
    # System managers have full access
    if "System Manager" in frappe.get_roles(user):
        return "full"
    
    # Check if owner
    workflow = frappe.get_doc("Automesh Workflow", workflow_id)
    if workflow.created_by == user or workflow.owner == user:
        return "full"
    
    # Check shares
    shares = frappe.get_all(
        "Automesh Workflow Share",
        filters={
            "workflow": workflow_id,
            "shared_with": user,
            "is_active": 1
        },
        fields=["permission_level", "expires_at"],
        order_by="permission_level desc"  # Get highest permission first
    )
    
    if shares:
        # Return highest non-expired permission
        for share in shares:
            if not share.expires_at or share.expires_at > now():
                return share.permission_level
    
    return None


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
