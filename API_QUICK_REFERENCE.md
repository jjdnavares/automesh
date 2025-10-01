# AutoMesh Workflow API - Quick Reference

**Phase 1 Implementation**  
**Last Updated:** 2025-10-01

---

## 📋 Available Endpoints

All endpoints are accessible via:
```
POST /api/method/automesh.automesh.api.workflow.<endpoint_name>
```

---

## 1. Get Workflows (List)

**Endpoint:** `get_workflows`

**Parameters:**
- `limit` (int, optional) - Number of results to return
- `offset` (int, optional) - Starting position for pagination
- `search` (string, optional) - Search in title and description
- `tags` (string, optional) - Comma-separated tags to filter by
- `is_active` (boolean, optional) - Filter by active status
- `sort_by` (string, optional) - Field to sort by (default: "modified")
- `sort_order` (string, optional) - "asc" or "desc" (default: "desc")

**Response:**
```json
{
  "workflows": [
    {
      "id": "Customer Onboarding Automation",
      "name": "Customer Onboarding Automation",
      "description": "Automatically onboard new customers...",
      "tags": "automation, customer, onboarding",
      "version": "1.0.0",
      "nodes": [...],
      "edges": [...],
      "metadata": {
        "createdAt": "2025-09-01 00:00:00",
        "updatedAt": "2025-09-26 00:00:00",
        "lastExecutedAt": "2025-10-01 00:00:00",
        "executionCount": 45,
        "isActive": true,
        "createdBy": "Administrator"
      }
    }
  ],
  "total": 8,
  "limit": null,
  "offset": null
}
```

**Examples:**
```python
# Get all workflows
get_workflows()

# Get first 10 workflows
get_workflows(limit=10, offset=0)

# Search for workflows
get_workflows(search="customer")

# Filter by tags
get_workflows(tags="automation,sales")

# Get only active workflows
get_workflows(is_active=True)

# Combined filters
get_workflows(limit=5, search="report", is_active=True, sort_by="execution_count", sort_order="desc")
```

---

## 2. Get Single Workflow

**Endpoint:** `get_workflow`

**Parameters:**
- `workflow_id` (string, required) - Workflow name/ID

**Response:**
```json
{
  "id": "Customer Onboarding Automation",
  "name": "Customer Onboarding Automation",
  "description": "Automatically onboard new customers...",
  "tags": "automation, customer, onboarding",
  "version": "1.0.0",
  "nodes": [
    {
      "id": "start-1",
      "type": "start",
      "position": {"x": 100, "y": 100},
      "data": {"label": "Start", "type": "start"}
    }
  ],
  "edges": [
    {
      "id": "e1",
      "source": "start-1",
      "target": "http-1"
    }
  ],
  "metadata": {
    "createdAt": "2025-09-01 00:00:00",
    "updatedAt": "2025-09-26 00:00:00",
    "lastExecutedAt": "2025-10-01 00:00:00",
    "executionCount": 45,
    "isActive": true,
    "createdBy": "Administrator"
  }
}
```

**Example:**
```python
get_workflow("Customer Onboarding Automation")
```

---

## 3. Create Workflow

**Endpoint:** `create_workflow`

**Request Body:**
```json
{
  "name": "My New Workflow",
  "description": "Description of the workflow",
  "tags": "automation, test",
  "version": "1.0.0",
  "nodes": [
    {
      "id": "start-1",
      "type": "start",
      "position": {"x": 100, "y": 100},
      "data": {"label": "Start", "type": "start"}
    }
  ],
  "edges": []
}
```

**Response:** Same as `get_workflow`

**Example:**
```python
import json
frappe.local.request = type('obj', (object,), {
    'data': json.dumps({
        "name": "My New Workflow",
        "description": "Test workflow",
        "tags": "test",
        "nodes": [],
        "edges": []
    })
})
create_workflow()
```

---

## 4. Update Workflow

**Endpoint:** `update_workflow`

**Request Body:**
```json
{
  "workflow_id": "My New Workflow",
  "workflow": {
    "name": "Updated Workflow Name",
    "description": "Updated description",
    "tags": "updated, tags",
    "version": "1.1.0",
    "nodes": [...],
    "edges": [...],
    "metadata": {
      "isActive": true
    }
  }
}
```

**Response:** Same as `get_workflow`

---

## 5. Delete Workflow

**Endpoint:** `delete_workflow`

**Request Body:**
```json
{
  "workflow_id": "Workflow to Delete"
}
```

**Response:**
```json
{
  "success": true
}
```

**Example:**
```python
import json
frappe.local.request = type('obj', (object,), {
    'data': json.dumps({
        "workflow_id": "Old Workflow"
    })
})
delete_workflow()
```

---

## 6. Duplicate Workflow

**Endpoint:** `duplicate_workflow`

**Request Body:**
```json
{
  "workflow_id": "Customer Onboarding Automation",
  "new_name": "Customer Onboarding Automation (Copy)"
}
```

**Response:** Same as `get_workflow`

**Notes:**
- If `new_name` is not provided, appends " (Copy)" to original name
- Sets `is_active` to false
- Resets `execution_count` to 0
- Resets `last_executed_at` to null
- Updates timestamps

**Example:**
```python
import json
frappe.local.request = type('obj', (object,), {
    'data': json.dumps({
        "workflow_id": "Customer Onboarding Automation",
        "new_name": "My Custom Copy"
    })
})
duplicate_workflow()
```

---

## 7. Toggle Workflow Status

**Endpoint:** `toggle_workflow_status`

**Request Body:**
```json
{
  "workflow_id": "Customer Onboarding Automation",
  "is_active": true
}
```

**Response:**
```json
{
  "success": true,
  "is_active": 1
}
```

**Example:**
```python
import json
frappe.local.request = type('obj', (object,), {
    'data': json.dumps({
        "workflow_id": "Customer Onboarding Automation",
        "is_active": False
    })
})
toggle_workflow_status()
```

---

## 8. Get Workflow Statistics

**Endpoint:** `get_workflow_statistics`

**Parameters:**
- `days` (int, optional) - Number of days to look back (default: 7)

**Response:**
```json
{
  "total_workflows": 8,
  "active_workflows": 6,
  "total_executions": 127,
  "completed": 120,
  "failed": 7,
  "failure_rate": "5.5%",
  "time_saved": "10.0h",
  "avg_runtime": "2.3s"
}
```

**Example:**
```python
# Last 7 days
get_workflow_statistics()

# Last 30 days
get_workflow_statistics(days=30)

# Last 90 days
get_workflow_statistics(days=90)
```

---

## 9. Get All Tags

**Endpoint:** `get_all_tags`

**Parameters:** None

**Response:**
```json
[
  "ai",
  "automation",
  "backup",
  "content",
  "customer",
  "email",
  "finance",
  "integration",
  "invoices",
  "leads",
  "maintenance",
  "marketing",
  "onboarding",
  "reporting",
  "sales",
  "sync"
]
```

**Example:**
```python
tags = get_all_tags()
print(f"Available tags: {', '.join(tags)}")
```

---

## 🔒 Permissions

### User Access
- Regular users can only access workflows they created (`created_by` field)
- System Managers can access all workflows

### Admin Operations
- Delete operations require System Manager role
- All other operations check ownership or System Manager role

---

## 🚨 Error Handling

All endpoints return proper error messages:

```json
{
  "exc_type": "ValidationError",
  "exception": "Workflow ID is required",
  "_server_messages": "[...]"
}
```

Common errors:
- `"Workflow ID is required"` - Missing workflow_id parameter
- `"You don't have permission to access this workflow"` - Permission denied
- `"You don't have permission to delete this workflow"` - Admin permission required

---

## 📊 Sample Data

The system includes 8 sample workflows:

1. **Customer Onboarding Automation** (Active, 45 executions)
2. **Daily Report Generator** (Active, 127 executions)
3. **Content Generation Pipeline** (Active, 23 executions)
4. **Invoice Processing Workflow** (Inactive, 8 executions)
5. **Data Sync Pipeline** (Active, 312 executions)
6. **Lead Qualification Bot** (Active, 89 executions)
7. **Backup Automation** (Inactive, 0 executions)
8. **Email Campaign Manager** (Active, 56 executions)

---

## 🧪 Testing

Run the test suite:
```bash
cd /home/jumes/bench-0/apps/automesh
bench --site automesh.localhost execute automesh.automesh.setup.test_phase1_api.execute
```

---

## 📝 Notes

- All timestamps are in format: `YYYY-MM-DD HH:MM:SS`
- Tags are stored as comma-separated strings
- Workflow JSON structure includes nodes and edges arrays
- Execution count is automatically incremented when workflow runs
- `last_executed_at` is updated on each execution

---

## 🔗 Related Documentation

- Full implementation details: `PHASE1_IMPLEMENTATION_SUMMARY.md`
- Feature checklist: `WORKFLOW_FEATURES_CHECKLIST.md`
- Dummy data script: `automesh/automesh/setup/add_dummy_workflows.py`
- Test suite: `automesh/automesh/setup/test_phase1_api.py`
