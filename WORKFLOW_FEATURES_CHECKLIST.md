# Workflow List Page - Features Implementation Checklist

**Project:** AutoMesh Workflow Management
**Framework:** Frappe + React + TypeScript
**Last Updated:** 2025-10-01 01:46 (Phase 1 Complete)

---

## 🎉 Phase 1: COMPLETED (2025-10-01)

**Status:** ✅ All backend APIs implemented and tested
**Test Results:** 7/7 tests passed (100%)
**Dummy Data:** 8 sample workflows created

### What's Done:
- ✅ Complete API implementation with pagination, filtering, search
- ✅ Duplicate workflow functionality
- ✅ Toggle workflow status
- ✅ Workflow statistics endpoint
- ✅ Tags management
- ✅ Comprehensive test suite
- ✅ Complete documentation (4 guides)
- ✅ 8 sample workflows with realistic data

### Documentation:
- `PHASE1_IMPLEMENTATION_SUMMARY.md` - Complete implementation details
- `API_QUICK_REFERENCE.md` - API documentation
- `FRONTEND_INTEGRATION_GUIDE.md` - Frontend integration guide
- `README_PHASE1.md` - Quick start guide

### Next: Frontend integration and Phase 2 features

---

## 📋 Overview

This document tracks the implementation of workflow list page functionalities, including required Frappe DocTypes, API endpoints, and frontend components.

---

## 🔧 Node Types Implementation Status

### ✅ Implemented Production Nodes (11 nodes)
**Location:** `automesh/automesh/workflow_engine/node_handlers.py`

#### **Core Workflow Nodes**
1. ✅ **start** - Workflow start node, passes input data to workflow
2. ✅ **end** - Workflow end node, sets final output
3. ✅ **condition** - Conditional branching with expression evaluation
4. ✅ **delay** - Pause workflow execution for specified duration

#### **HTTP & API Nodes**
5. ✅ **http_request** - Make HTTP requests (GET, POST, PUT, PATCH, DELETE)
   - Supports headers, params, body, timeout
   - Returns status code, headers, and response data

#### **Data Transformation Nodes**
6. ✅ **transform** - Data transformation with multiple modes:
   - **map** - Field mapping and nested path extraction
   - **filter** - Array filtering with expressions
   - **reduce** - Array reduction operations
   - **custom** - Custom script execution

#### **Frappe Integration Nodes**
7. ✅ **frappe_doc_create** - Create Frappe documents
8. ✅ **frappe_doc_update** - Update Frappe documents
9. ✅ **frappe_doc_get** - Retrieve Frappe documents with field selection
10. ✅ **frappe_doc_delete** - Delete Frappe documents
11. ✅ **frappe_doc_list** - Query/list Frappe documents with filters

---

### ✅ Implemented Test Nodes (6 nodes)
**Location:** `automesh/automesh/workflow_engine/test_node_types.py`

1. ✅ **test_echo** - Echo input to output with timestamp
2. ✅ **test_random** - Generate random data (number, float, boolean, string, array, object)
3. ✅ **test_delay** - Test delay functionality
4. ✅ **test_math** - Math operations (add, subtract, multiply, divide, power, modulo)
5. ✅ **test_error** - Error handling testing (standard, exception, division_by_zero, key_error)
6. ✅ **test_transform** - Data transformations (uppercase, lowercase, capitalize, reverse, length, JSON, increment, etc.)

---

### ✅ Implemented Writer Integration Nodes (3 nodes) 🆕
**Location:** `automesh/automesh/workflow_engine/writer_nodes.py`
**Status:** ✅ Production Ready (Implemented: 2025-10-01)
**Integration:** Writer App (LLM Content Generation)

#### **AI/Content Generation Nodes**
1. ✅ **writer_generate_content** - Generate content using Writer app's LLM providers
   - Supports 11+ LLM providers (OpenAI, Anthropic, Google, Groq, Mistral, Ollama, etc.)
   - 7 content types (Blog Post, Article, Product Description, Landing Page, etc.)
   - 6 tone options (Professional, Casual, Friendly, Formal, Humorous, Technical)
   - Automatic content humanization (two-pass generation)
   - Auto-saves to Generated Content DocType

2. ✅ **writer_custom_prompt** - Custom prompt execution with LLM
   - Direct LLM access without templates
   - Support for dynamic placeholders from input data
   - Maximum flexibility for specialized use cases
   - All Writer providers supported

3. ✅ **writer_get_content** - Retrieve generated content
   - Fetch specific content by document name
   - List multiple contents with filters
   - Filter by keyword or content type
   - Pagination support

**Setup Script:** `automesh/automesh/workflow_engine/setup_writer_nodes.py`
**Test Suite:** `automesh/automesh/workflow_engine/test_writer_nodes.py`
**Documentation:** `WRITER_NODES_README.md`, `WRITER_NODES_IMPLEMENTATION.md`

---

### ⚠️ Important Nodes NOT Yet Implemented

#### **High Priority - Essential Workflow Nodes**

1. ⚠️ **loop** / **for_each** - Iterate over arrays/collections
   - Loop through items
   - Execute sub-workflow for each item
   - Collect results
   - Support break/continue logic

2. ⚠️ **parallel** - Execute multiple branches in parallel
   - Run multiple nodes simultaneously
   - Wait for all to complete
   - Aggregate results

3. ⚠️ **merge** - Merge multiple data streams
   - Combine outputs from multiple nodes
   - Support different merge strategies (first, last, all, custom)

4. ⚠️ **switch** - Multi-way branching
   - Route to different paths based on value
   - Like switch/case statement
   - Default fallback path

5. ⚠️ **set_variable** - Set workflow variables
   - Store intermediate results
   - Share data across nodes

6. ⚠️ **get_variable** - Retrieve workflow variables
   - Access stored values
   - Support default values

#### **Medium Priority - Data & Integration Nodes**

7. ⚠️ **json_parse** - Parse JSON strings
8. ⚠️ **json_stringify** - Convert to JSON string
9. ⚠️ **xml_parse** - Parse XML data
10. ⚠️ **xml_build** - Build XML from data
11. ⚠️ **csv_parse** - Parse CSV data
12. ⚠️ **csv_build** - Build CSV from data
13. ⚠️ **template** - Template rendering (Jinja2)
14. ⚠️ **regex** - Regular expression operations
15. ⚠️ **code** - Execute custom Python code safely
16. ⚠️ **function** - Reusable sub-workflow/function call

#### **Medium Priority - External Integrations**

17. ⚠️ **email_send** - Send emails via SMTP
18. ⚠️ **email_read** - Read emails via IMAP
19. ⚠️ **webhook** - Trigger webhook/HTTP callback
20. ⚠️ **schedule** - Schedule delayed execution
21. ⚠️ **file_read** - Read file from storage
22. ⚠️ **file_write** - Write file to storage
23. ⚠️ **file_upload** - Upload file to external service
24. ⚠️ **database_query** - Execute database queries
25. ⚠️ **redis_get** / **redis_set** - Redis operations

#### **Medium Priority - AI/ML Nodes**

26. ✅ **writer_generate_content** - Multi-provider LLM content generation (IMPLEMENTED - see above)
27. ✅ **writer_custom_prompt** - Custom LLM prompts (IMPLEMENTED - see above)
28. ⚠️ **openai_embedding** - Generate embeddings
29. ⚠️ **text_analyze** - Text analysis (sentiment, keywords)
30. ⚠️ **image_process** - Image processing operations
31. ⚠️ **writer_summarize** - Content summarization (Planned - Phase 2)
32. ⚠️ **writer_translate** - Content translation (Planned - Phase 2)
33. ⚠️ **writer_rewrite** - Content rewriting (Planned - Phase 2)
34. ⚠️ **writer_extract_keywords** - Keyword extraction (Planned - Phase 2)

#### **Low Priority - Utility Nodes**

32. ⚠️ **logger** - Advanced logging node
33. ⚠️ **counter** - Increment/decrement counters
34. ⚠️ **cache_get** / **cache_set** - Caching operations
35. ⚠️ **hash** - Generate hashes (MD5, SHA256)
36. ⚠️ **encrypt** / **decrypt** - Encryption operations
37. ⚠️ **compress** / **decompress** - Data compression
38. ⚠️ **date_format** - Date/time formatting
39. ⚠️ **math_advanced** - Advanced math (sin, cos, log, etc.)
40. ⚠️ **random_uuid** - Generate UUIDs

#### **Low Priority - Notification Nodes**

41. ⚠️ **slack_message** - Send Slack messages
42. ⚠️ **discord_message** - Send Discord messages
43. ⚠️ **telegram_message** - Send Telegram messages
44. ⚠️ **sms_send** - Send SMS messages
45. ⚠️ **push_notification** - Send push notifications

#### **Low Priority - Cloud Service Nodes**

46. ⚠️ **aws_s3** - AWS S3 operations
47. ⚠️ **google_drive** - Google Drive operations
48. ⚠️ **dropbox** - Dropbox operations
49. ⚠️ **github** - GitHub API operations
50. ⚠️ **stripe** - Stripe payment operations

---

### 📊 Node Implementation Summary

- **Total Implemented:** 20 nodes (11 production + 6 test + 3 Writer integration) ✅
- **Writer Integration:** 3 nodes (Generate Content, Custom Prompt, Get Content) 🆕
- **High Priority Missing:** 6 nodes (loop, parallel, merge, switch, set_variable, get_variable)
- **Medium Priority Missing:** 21 nodes (data, integration, 2 AI/ML implemented via Writer)
- **Low Priority Missing:** 19 nodes (utility, notifications, cloud services)
- **Total Planned:** 70+ nodes

**Recent Addition (2025-10-01):**
- ✅ Writer app integration complete with 3 production-ready nodes
- ✅ Multi-provider LLM support (11+ providers)
- ✅ Content generation, custom prompts, and content retrieval
- 📝 Documentation: `WRITER_NODES_README.md`, `WRITER_NODES_IMPLEMENTATION.md`

---

## 🗄️ Existing Frappe DocTypes

### ✅ Automesh Workflow
**Status:** Already exists
**Location:** `automesh/automesh/doctype/automesh_workflow/`

**Fields:**
- `title` (Data, Required, Unique) - Workflow name
- `description` (Text Editor) - Detailed description
- `version` (Data) - Version number (default: "1.0.0")
- `is_active` (Check) - Active status
- `tags` (Small Text) - Tags for categorization
- `created_at` (Datetime) - Creation timestamp
- `updated_at` (Datetime) - Last update timestamp
- `last_executed_at` (Datetime) - Last execution timestamp
- `execution_count` (Int) - Number of executions
- `workflow_json` (Code) - Complete workflow data (nodes & edges)
- `created_by` (Link to User) - Creator

**Permissions:** System Manager (full access)

---

### ✅ Automesh Execution
**Status:** Already exists
**Location:** `automesh/automesh/doctype/automesh_execution/`

**Fields:**
- `workflow` (Link to Automesh Workflow, Required) - Parent workflow
- `status` (Select) - draft/queued/running/completed/failed/paused/cancelled
- `start_time` (Datetime) - Execution start time
- `end_time` (Datetime) - Execution end time
- `input_data` (Code) - Input JSON
- `output_data` (Code) - Output JSON
- `execution_data` (Code) - Intermediate data
- `error_message` (Long Text) - Error details
- `created_by` (Link to User) - Executor

**Naming:** `AMWF-{workflow}-{#####}`
**Permissions:** System Manager (full access)

---

### ✅ Automesh Template
**Status:** Already exists
**Location:** `automesh/automesh/doctype/automesh_template/`

**Fields:**
- `title` (Data, Required, Unique) - Template name
- `description` (Text Editor) - Description
- `category` (Select) - automation/content/communication/integration
- `tags` (Small Text) - Tags
- `version` (Data) - Version (default: "1.0.0")
- `is_featured` (Check) - Featured status
- `template_json` (Code, Required) - Template definition
- `created_by` (Link to User) - Creator

**Permissions:** System Manager (full access)

---

### ✅ Automesh Node Type
**Status:** Already exists
**Location:** `automesh/automesh/doctype/automesh_node_type/`

**Fields:**
- `type` (Data, Required, Unique) - Node type identifier
- `label` (Data, Required) - Display label
- `description` (Text) - Description
- `icon` (Data) - Icon identifier
- `color` (Data) - Color code
- `category` (Select) - automation/content/communication/integration
- `inputs` (Small Text) - Input specs (JSON)
- `outputs` (Small Text) - Output specs (JSON)
- `is_system` (Check) - System node flag
- `is_enabled` (Check) - Enabled status
- `handler_module` (Data) - Python module path
- `handler_function` (Data) - Handler function name
- `schema_json` (Code) - Parameter schema
- `created_by` (Link to User) - Creator

**Permissions:** System Manager (full access)

---

## 🆕 New DocTypes Required

### ⚠️ Automesh Workflow Share
**Status:** NEEDS TO BE CREATED
**Purpose:** Manage workflow sharing and permissions between users

**Recommended Configuration:**

```json
{
  "doctype": "DocType",
  "name": "Automesh Workflow Share",
  "module": "AutoMesh",
  "istable": 0,
  "is_submittable": 0,
  "autoname": "format:AMWFS-{#####}",
  "naming_rule": "Expression",
  "track_changes": 1,
  "fields": [
    {
      "fieldname": "workflow",
      "fieldtype": "Link",
      "label": "Workflow",
      "options": "Automesh Workflow",
      "reqd": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "shared_with",
      "fieldtype": "Link",
      "label": "Shared With",
      "options": "User",
      "reqd": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "permission_level",
      "fieldtype": "Select",
      "label": "Permission Level",
      "options": "view\nexecute\nedit\nfull",
      "default": "view",
      "reqd": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "shared_by",
      "fieldtype": "Link",
      "label": "Shared By",
      "options": "User",
      "reqd": 1
    },
    {
      "fieldname": "shared_at",
      "fieldtype": "Datetime",
      "label": "Shared At",
      "default": "now"
    },
    {
      "fieldname": "expires_at",
      "fieldtype": "Datetime",
      "label": "Expires At"
    },
    {
      "fieldname": "is_active",
      "fieldtype": "Check",
      "label": "Is Active",
      "default": 1
    }
  ],
  "permissions": [
    {
      "role": "System Manager",
      "read": 1,
      "write": 1,
      "create": 1,
      "delete": 1
    }
  ]
}
```

**Implementation Steps:**
1. Create DocType via Frappe UI or bench command
2. Add validation to prevent duplicate shares
3. Add permission checks in workflow API endpoints

---

### ⚠️ Automesh Workflow Tag
**Status:** NEEDS TO BE CREATED (Optional - can use existing tags field)
**Purpose:** Better tag management with autocomplete

**Recommended Configuration:**

```json
{
  "doctype": "DocType",
  "name": "Automesh Workflow Tag",
  "module": "AutoMesh",
  "istable": 0,
  "autoname": "field:tag_name",
  "naming_rule": "By fieldname",
  "fields": [
    {
      "fieldname": "tag_name",
      "fieldtype": "Data",
      "label": "Tag Name",
      "reqd": 1,
      "unique": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "color",
      "fieldtype": "Color",
      "label": "Color"
    },
    {
      "fieldname": "usage_count",
      "fieldtype": "Int",
      "label": "Usage Count",
      "default": 0,
      "read_only": 1
    }
  ],
  "permissions": [
    {
      "role": "System Manager",
      "read": 1,
      "write": 1,
      "create": 1,
      "delete": 1
    }
  ]
}
```

**Note:** This is optional. The existing `tags` field in Automesh Workflow can be used with comma-separated values.

---

## 🎯 Feature Implementation Checklist

### Phase 1: Core CRUD Operations

#### ✅ 1.1 Fetch Workflows from API
- [x] **Backend API** (`automesh/api/workflow.py`)
  - [x] `get_workflows()` endpoint exists
  - [x] Add pagination support (limit, offset)
  - [x] Add filtering by tags
  - [x] Add search by title/description
  - [x] Add sorting options
  - [x] Optimize query performance
  - [x] Returns total count for pagination

- [ ] **Frontend Service** (`frontend/src/services/workflow/workflowApi.ts`)
  - [ ] Update `getWorkflows()` to handle query parameters
  - [ ] Add TypeScript interfaces for filters
  - [ ] Handle loading states
  - [ ] Handle error states

- [ ] **Frontend Store** (`frontend/src/store/workflow/workflowStore.ts`)
  - [x] `fetchWorkflows()` method exists
  - [ ] Add filter state management
  - [ ] Add pagination state
  - [ ] Cache workflows locally

- [ ] **Frontend UI** (`frontend/src/pages/workflow/WorkflowListPage.tsx`)
  - [ ] Call `fetchWorkflows()` on component mount
  - [ ] Replace sample data with real data
  - [ ] Show loading spinner
  - [ ] Show error messages
  - [ ] Add empty state handling

**Estimated Time:** 3-4 hours

---

#### ✅ 1.2 Delete Workflow
- [x] **Backend API** (`automesh/api/workflow.py`)
  - [x] `delete_workflow()` endpoint exists
  - [x] Add permission checks
  - [x] Requires admin/owner permissions
  - [ ] Add cascade delete for executions (optional - Phase 2)
  - [ ] Add soft delete option (optional - Phase 2)

- [ ] **Frontend Service**
  - [ ] Implement `deleteWorkflow(id)` API call

- [ ] **Frontend Store**
  - [x] `deleteWorkflow()` method exists
  - [ ] Update local state after deletion
  - [ ] Refresh workflow list

- [ ] **Frontend UI**
  - [ ] Wire up delete button
  - [ ] Add confirmation dialog component
  - [ ] Show success/error toast
  - [ ] Disable button during deletion
  - [ ] Handle optimistic updates

**Estimated Time:** 2-3 hours

---

#### ✅ 1.3 Duplicate/Copy Workflow
- [x] **Backend API** (`automesh/api/workflow.py`)
  - [x] Create `duplicate_workflow()` endpoint
  - [x] Copy workflow with new name (append "Copy")
  - [x] Reset execution count
  - [x] Set is_active to false
  - [x] Update timestamps

```python
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
```

- [ ] **Frontend Service**
  - [ ] Implement `duplicateWorkflow(id, newName?)` API call

- [ ] **Frontend Store**
  - [ ] Add `duplicateWorkflow()` method
  - [ ] Add to workflows map
  - [ ] Optionally navigate to new workflow

- [ ] **Frontend UI**
  - [ ] Wire up copy button
  - [ ] Add name input dialog (optional)
  - [ ] Show success toast
  - [ ] Navigate to duplicated workflow

**Estimated Time:** 2-3 hours

---

#### ✅ 1.4 Toggle Workflow Active Status
- [x] **Backend API** (`automesh/api/workflow.py`)
  - [x] Create `toggle_workflow_status()` endpoint
  - [x] Update `is_active` field
  - [x] Add validation rules
  - [x] Update timestamps

```python
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
```

- [ ] **Frontend Service**
  - [ ] Implement `toggleWorkflowStatus(id, isActive)` API call

- [ ] **Frontend Store**
  - [ ] Add `toggleWorkflowStatus()` method
  - [ ] Update local workflow state

- [ ] **Frontend UI**
  - [ ] Make badge clickable or add toggle switch
  - [ ] Update UI optimistically
  - [ ] Show success/error feedback

**Estimated Time:** 1-2 hours

---

### Phase 2: Enhanced Features

#### ✅ 2.1 Bulk Operations
- [ ] **Frontend UI**
  - [ ] Add checkbox selection to workflow cards
  - [ ] Add "Select All" checkbox
  - [ ] Add bulk action toolbar
  - [ ] Implement bulk delete
  - [ ] Implement bulk activate/deactivate
  - [ ] Add confirmation for bulk actions

- [ ] **Backend API**
  - [ ] Create `bulk_delete_workflows()` endpoint
  - [ ] Create `bulk_update_status()` endpoint
  - [ ] Add transaction handling

**Estimated Time:** 4-5 hours

---

#### ✅ 2.2 Quick Execute from List
- [ ] **Frontend UI**
  - [ ] Add "Run" button to workflow cards
  - [ ] Show inline execution status
  - [ ] Add execution progress indicator
  - [ ] Link to execution details

- [ ] **Backend API**
  - [x] `execute_workflow()` endpoint exists
  - [ ] Add quick execute with default inputs

**Estimated Time:** 3-4 hours

---

#### ✅ 2.3 Enhanced Statistics Dashboard
- [ ] **Backend API** (`automesh/api/workflow.py`)
  - [ ] Create `get_workflow_statistics()` endpoint
  - [ ] Calculate real metrics from executions
  - [ ] Add time range filters (7d, 30d, 90d)

```python
@frappe.whitelist()
def get_workflow_statistics(days=7):
    """Get workflow statistics for dashboard"""
    user = frappe.session.user
    is_admin = "System Manager" in frappe.get_roles()
    
    # Date range
    from_date = frappe.utils.add_days(now(), -days)
    
    # Get executions in date range
    filters = {"start_time": [">=", from_date]}
    if not is_admin:
        # Filter by user's workflows
        user_workflows = frappe.get_all(
            "Automesh Workflow",
            filters={"created_by": user},
            pluck="name"
        )
        filters["workflow"] = ["in", user_workflows]
    
    executions = frappe.get_all(
        "Automesh Execution",
        filters=filters,
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
        "total_executions": total_executions,
        "completed": completed,
        "failed": failed,
        "failure_rate": f"{failure_rate:.1f}%",
        "time_saved": f"{time_saved_hours:.1f}h",
        "avg_runtime": f"{avg_runtime:.1f}s",
        "active_workflows": frappe.db.count("Automesh Workflow", {"is_active": 1})
    }
```

- [ ] **Frontend Service**
  - [ ] Implement `getWorkflowStatistics(days)` API call

- [ ] **Frontend UI**
  - [ ] Update Overview card with real data
  - [ ] Add time range selector
  - [ ] Add more metric cards
  - [ ] Add charts/graphs (optional)

**Estimated Time:** 4-5 hours

---

#### ✅ 2.4 Workflow Templates
- [ ] **Backend API** (`automesh/api/workflow.py`)
  - [ ] Create `get_templates()` endpoint
  - [ ] Create `create_workflow_from_template()` endpoint

```python
@frappe.whitelist()
def get_templates(category=None):
    """Get available workflow templates"""
    filters = {"is_featured": 1} if not category else {"category": category}
    
    templates = frappe.get_all(
        "Automesh Template",
        filters=filters,
        fields=["name", "title", "description", "category", "tags", "version"]
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
    template_data = json.loads(template.template_json)
    
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
```

- [ ] **Frontend UI**
  - [ ] Add "Create from Template" button
  - [ ] Create template gallery modal
  - [ ] Show template preview
  - [ ] Filter templates by category

**Estimated Time:** 5-6 hours

---

#### ✅ 2.5 Import/Export Workflows
- [ ] **Backend API** (`automesh/api/workflow.py`)
  - [ ] Create `export_workflow()` endpoint (returns JSON)
  - [ ] Create `import_workflow()` endpoint (accepts JSON)
  - [ ] Add validation for imported data

```python
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
```

- [ ] **Frontend Store**
  - [x] `exportWorkflow()` method exists
  - [x] `importWorkflow()` method exists
  - [ ] Connect to backend APIs

- [ ] **Frontend UI**
  - [ ] Add "Export" button to workflow cards
  - [ ] Add "Import" button to page header
  - [ ] Handle file download
  - [ ] Handle file upload
  - [ ] Show import preview

**Estimated Time:** 3-4 hours

---

#### ✅ 2.6 Workflow Sharing & Permissions
- [ ] **Create DocType**
  - [ ] Create "Automesh Workflow Share" DocType (see configuration above)

- [ ] **Backend API** (`automesh/api/workflow.py`)
  - [ ] Create `share_workflow()` endpoint
  - [ ] Create `get_workflow_shares()` endpoint
  - [ ] Create `revoke_workflow_share()` endpoint
  - [ ] Update `_can_access_workflow()` to check shares

```python
def _can_access_workflow(workflow_id, require_admin=False):
    """Check if user can access workflow"""
    user = frappe.session.user
    
    # System Manager can access all
    if "System Manager" in frappe.get_roles():
        return True
    
    workflow = frappe.get_doc("Automesh Workflow", workflow_id)
    
    # Owner can access
    if workflow.created_by == user:
        return True
    
    # Check if shared with user
    shares = frappe.get_all(
        "Automesh Workflow Share",
        filters={
            "workflow": workflow_id,
            "shared_with": user,
            "is_active": 1
        },
        fields=["permission_level"]
    )
    
    if shares:
        if require_admin:
            return any(s.permission_level == "full" for s in shares)
        return True
    
    return False

@frappe.whitelist()
def share_workflow():
    """Share workflow with another user"""
    data = json.loads(frappe.request.data)
    workflow_id = data.get("workflow_id")
    shared_with = data.get("shared_with")
    permission_level = data.get("permission_level", "view")
    
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
        share.save()
    else:
        # Create new share
        share = frappe.new_doc("Automesh Workflow Share")
        share.workflow = workflow_id
        share.shared_with = shared_with
        share.permission_level = permission_level
        share.shared_by = frappe.session.user
        share.shared_at = now()
        share.is_active = 1
        share.insert()
    
    return {"success": True}
```

- [ ] **Frontend UI**
  - [ ] Add "Share" button to workflow cards
  - [ ] Create share dialog with user selector
  - [ ] Show permission level options
  - [ ] List current shares
  - [ ] Allow revoking shares

**Estimated Time:** 6-8 hours

---

#### ✅ 2.7 Execution History View
- [ ] **Backend API** (`automesh/api/workflow.py`)
  - [ ] Create `get_workflow_executions()` endpoint
  - [ ] Add pagination and filtering

```python
@frappe.whitelist()
def get_workflow_executions(workflow_id, limit=10, offset=0):
    """Get execution history for a workflow"""
    if not workflow_id:
        frappe.throw(_("Workflow ID is required"))
    
    if not _can_access_workflow(workflow_id):
        frappe.throw(_("You don't have permission to access this workflow"))
    
    executions = frappe.get_all(
        "Automesh Execution",
        filters={"workflow": workflow_id},
        fields=["name", "status", "start_time", "end_time", "created_by"],
        order_by="start_time desc",
        limit=limit,
        start=offset
    )
    
    total = frappe.db.count("Automesh Execution", {"workflow": workflow_id})
    
    return {
        "executions": executions,
        "total": total,
        "limit": limit,
        "offset": offset
    }
```

- [ ] **Frontend UI**
  - [ ] Add "View Executions" button/link
  - [ ] Create execution history modal or page
  - [ ] Show execution list with status badges
  - [ ] Add pagination
  - [ ] Link to detailed execution view

**Estimated Time:** 4-5 hours

---

#### ✅ 2.8 Tags & Categories
- [ ] **Backend API** (`automesh/api/workflow.py`)
  - [ ] Create `get_all_tags()` endpoint
  - [ ] Update `get_workflows()` to filter by tags

```python
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
```

- [ ] **Frontend UI**
  - [ ] Add tag filter dropdown
  - [ ] Show tags on workflow cards
  - [ ] Make tags clickable to filter
  - [ ] Add tag input with autocomplete in create form

**Estimated Time:** 3-4 hours

---

### Phase 3: Polish & Optimization

#### ✅ 3.1 Performance Optimization
- [ ] **Backend**
  - [ ] Add database indexes
  - [ ] Implement caching for frequently accessed data
  - [ ] Optimize queries with proper joins
  - [ ] Add pagination to all list endpoints

- [ ] **Frontend**
  - [ ] Implement virtual scrolling for large lists
  - [ ] Add debouncing to search input
  - [ ] Lazy load workflow details
  - [ ] Cache API responses

**Estimated Time:** 4-5 hours

---

#### ✅ 3.2 UI/UX Enhancements
- [ ] **Frontend UI**
  - [ ] Add skeleton loaders
  - [ ] Improve error messages
  - [ ] Add keyboard shortcuts
  - [ ] Add tooltips for actions
  - [ ] Improve mobile responsiveness
  - [ ] Add animations/transitions
  - [ ] Add confirmation dialogs for destructive actions

**Estimated Time:** 4-5 hours

---

#### ✅ 3.3 Testing
- [ ] **Backend Tests**
  - [ ] Unit tests for API endpoints
  - [ ] Permission tests
  - [ ] Data validation tests

- [ ] **Frontend Tests**
  - [ ] Component tests
  - [ ] Integration tests
  - [ ] E2E tests for critical flows

**Estimated Time:** 6-8 hours

---

## 📊 Priority Ranking

### 🔴 High Priority (Must Have)
1. Fetch Workflows from API (1.1)
2. Delete Workflow (1.2)
3. Enhanced Statistics (2.3)
4. Duplicate Workflow (1.3)

### 🟡 Medium Priority (Should Have)
5. Toggle Active Status (1.4)
6. Quick Execute (2.2)
7. Execution History (2.7)
8. Tags & Categories (2.8)

### 🟢 Low Priority (Nice to Have)
9. Bulk Operations (2.1)
10. Templates (2.4)
11. Import/Export (2.5)
12. Sharing & Permissions (2.6)

### 🔵 Polish (Future)
13. Performance Optimization (3.1)
14. UI/UX Enhancements (3.2)
15. Testing (3.3)

---

## 📈 Estimated Total Time

- **Phase 1 (Core CRUD):** 12-16 hours
- **Phase 2 (Enhanced Features):** 28-36 hours
- **Phase 3 (Polish):** 14-18 hours

**Total:** 54-70 hours (~7-9 working days)

---

## 🚀 Getting Started

### Recommended Implementation Order:

1. **Day 1-2:** Implement 1.1 (Fetch Workflows) + 1.2 (Delete)
2. **Day 2-3:** Implement 1.3 (Duplicate) + 1.4 (Toggle Status)
3. **Day 3-4:** Implement 2.3 (Enhanced Statistics) + 2.8 (Tags)
4. **Day 4-5:** Implement 2.2 (Quick Execute) + 2.7 (Execution History)
5. **Day 5-6:** Implement 2.4 (Templates) + 2.5 (Import/Export)
6. **Day 6-7:** Implement 2.6 (Sharing) + 2.1 (Bulk Operations)
7. **Day 7-9:** Phase 3 (Polish, Optimization, Testing)

---

## 📝 Notes

- All API endpoints should follow RESTful conventions
- Use Frappe's built-in permission system where possible
- Maintain backward compatibility with existing data
- Add proper error handling and validation
- Document all new endpoints
- Follow existing code style and patterns
- Test on both desktop and mobile viewports

---

## 🔗 Related Files

- **Backend API:** `automesh/automesh/api/workflow.py`
- **Frontend Store:** `frontend/src/store/workflow/workflowStore.ts`
- **Frontend Service:** `frontend/src/services/workflow/workflowApi.ts`
- **Frontend Page:** `frontend/src/pages/workflow/WorkflowListPage.tsx`
- **DocTypes:** `automesh/automesh/doctype/`

---

**Last Updated:** 2025-10-01
**Maintained By:** Development Team
