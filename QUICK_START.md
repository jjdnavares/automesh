# AutoMesh Phase 1 - Quick Start Guide

**Last Updated:** 2025-10-01 01:46  
**Status:** ✅ Production Ready

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Add Dummy Data (30 seconds)

```bash
cd /home/jumes/bench-0/apps/automesh
bench --site automesh.localhost execute automesh.automesh.setup.add_dummy_workflows.execute
```

**Expected Output:**
```
============================================================
Creating Dummy Workflows for Phase 1 Testing
============================================================
✅ Created workflow: Customer Onboarding Automation
✅ Created workflow: Daily Report Generator
✅ Created workflow: Content Generation Pipeline
✅ Created workflow: Invoice Processing Workflow
✅ Created workflow: Data Sync Pipeline
✅ Created workflow: Lead Qualification Bot
✅ Created workflow: Backup Automation
✅ Created workflow: Email Campaign Manager

✅ Successfully created 8 workflows
Total workflows in database: 8
```

---

### Step 2: Run Tests (1 minute)

```bash
bench --site automesh.localhost execute automesh.automesh.setup.test_phase1_api.execute
```

**Expected Output:**
```
============================================================
PHASE 1 API ENDPOINT TESTS
============================================================

Testing: get_workflows()
✅ Fetched 8 workflows
✅ Pagination works: 3 workflows (limit=3)
✅ Search works: Found 1 workflows with 'customer'
✅ Tag filter works: Found 8 workflows with 'automation' tag
✅ Active filter works: Found 6 active workflows

Testing: get_workflow()
✅ Fetched workflow: Email Campaign Manager

Testing: duplicate_workflow()
✅ Duplicated workflow: Test Duplicate Workflow
✅ Cleaned up test duplicate

Testing: toggle_workflow_status()
✅ Toggled status: 0 (expected: False)
✅ Restored status: 1 (expected: True)

Testing: get_workflow_statistics()
✅ Statistics retrieved:
   Total workflows: 8
   Active workflows: 6

Testing: get_all_tags()
✅ Retrieved 16 unique tags

Testing: delete_workflow()
✅ Created test workflow: Test Workflow to Delete
✅ Deleted workflow: True

============================================================
TEST SUMMARY
============================================================
✅ PASS: Get Workflows
✅ PASS: Get Single Workflow
✅ PASS: Duplicate Workflow
✅ PASS: Toggle Workflow Status
✅ PASS: Get Workflow Statistics
✅ PASS: Get All Tags
✅ PASS: Delete Workflow

7/7 tests passed
```

---

### Step 3: Test API Manually (2 minutes)

#### Open Frappe Console:
```bash
bench --site automesh.localhost console
```

#### Test Commands:

```python
# Import API functions
from automesh.automesh.api.workflow import *

# 1. Get all workflows
workflows = get_workflows()
print(f"Total workflows: {workflows['total']}")
print(f"First workflow: {workflows['workflows'][0]['name']}")

# 2. Get workflows with filters
active = get_workflows(is_active=True)
print(f"Active workflows: {len(active['workflows'])}")

# 3. Search workflows
results = get_workflows(search="customer")
print(f"Search results: {len(results['workflows'])}")

# 4. Get statistics
stats = get_workflow_statistics(days=7)
print(f"Statistics: {stats}")

# 5. Get all tags
tags = get_all_tags()
print(f"Tags: {tags}")

# 6. Get single workflow
workflow = get_workflow("Customer Onboarding Automation")
print(f"Workflow: {workflow['name']}")
print(f"Nodes: {len(workflow['nodes'])}")
print(f"Edges: {len(workflow['edges'])}")

# Exit console
exit()
```

---

## 📊 What You Get

### 8 Sample Workflows

1. **Customer Onboarding Automation** (Active)
   - Executions: 45
   - Tags: automation, customer, onboarding
   - Nodes: 4 (start → http_request → frappe_doc_create → end)

2. **Daily Report Generator** (Active)
   - Executions: 127
   - Tags: reporting, automation, sales
   - Nodes: 4 (start → frappe_doc_list → transform → end)

3. **Content Generation Pipeline** (Active)
   - Executions: 23
   - Tags: content, ai, automation
   - Nodes: 4 (start → writer_generate_content → frappe_doc_create → end)

4. **Invoice Processing Workflow** (Inactive)
   - Executions: 8
   - Tags: finance, automation, invoices
   - Nodes: 5 (with condition branching)

5. **Data Sync Pipeline** (Active)
   - Executions: 312
   - Tags: integration, sync, automation
   - Nodes: 5 (full ETL pipeline)

6. **Lead Qualification Bot** (Active)
   - Executions: 89
   - Tags: sales, automation, leads
   - Nodes: 4 (with condition logic)

7. **Backup Automation** (Inactive)
   - Executions: 0
   - Tags: backup, automation, maintenance
   - Nodes: 4 (data backup flow)

8. **Email Campaign Manager** (Active)
   - Executions: 56
   - Tags: email, marketing, automation
   - Nodes: 5 (subscriber management)

---

## 🔧 API Endpoints Available

### 1. Get Workflows (with filters)
```python
get_workflows(
    limit=10,           # Optional: number of results
    offset=0,           # Optional: pagination offset
    search="customer",  # Optional: search term
    tags="automation",  # Optional: filter by tags
    is_active=True,     # Optional: filter by status
    sort_by="modified", # Optional: sort field
    sort_order="desc"   # Optional: sort direction
)
```

### 2. Get Single Workflow
```python
get_workflow("Customer Onboarding Automation")
```

### 3. Create Workflow
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

### 4. Update Workflow
```python
frappe.local.request = type('obj', (object,), {
    'data': json.dumps({
        "workflow_id": "My New Workflow",
        "workflow": {
            "name": "Updated Name",
            "description": "Updated description"
        }
    })
})
update_workflow()
```

### 5. Delete Workflow
```python
frappe.local.request = type('obj', (object,), {
    'data': json.dumps({
        "workflow_id": "My New Workflow"
    })
})
delete_workflow()
```

### 6. Duplicate Workflow
```python
frappe.local.request = type('obj', (object,), {
    'data': json.dumps({
        "workflow_id": "Customer Onboarding Automation",
        "new_name": "My Copy"
    })
})
duplicate_workflow()
```

### 7. Toggle Status
```python
frappe.local.request = type('obj', (object,), {
    'data': json.dumps({
        "workflow_id": "Customer Onboarding Automation",
        "is_active": False
    })
})
toggle_workflow_status()
```

### 8. Get Statistics
```python
get_workflow_statistics(days=7)  # Last 7 days
get_workflow_statistics(days=30) # Last 30 days
```

### 9. Get All Tags
```python
get_all_tags()
```

---

## 🧪 Verify Everything Works

### Check Database
```bash
bench --site automesh.localhost console
```

```python
import frappe

# Count workflows
count = frappe.db.count("Automesh Workflow")
print(f"Total workflows: {count}")  # Should be 8

# List all workflows
workflows = frappe.get_all("Automesh Workflow", fields=["name", "is_active", "execution_count"])
for w in workflows:
    print(f"- {w.name} (Active: {w.is_active}, Executions: {w.execution_count})")

# Get active workflows
active = frappe.db.count("Automesh Workflow", {"is_active": 1})
print(f"Active workflows: {active}")  # Should be 6

exit()
```

---

## 📚 Documentation

### Main Guides

1. **[README_PHASE1.md](./README_PHASE1.md)**
   - Overview and quick start
   - What's implemented
   - How to use

2. **[PHASE1_IMPLEMENTATION_SUMMARY.md](./PHASE1_IMPLEMENTATION_SUMMARY.md)**
   - Complete technical details
   - Database schema
   - Test results
   - Security considerations

3. **[API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md)**
   - All API endpoints
   - Request/response examples
   - Parameter documentation

4. **[FRONTEND_INTEGRATION_GUIDE.md](./FRONTEND_INTEGRATION_GUIDE.md)**
   - React/TypeScript integration
   - Complete code examples
   - State management
   - UI components

### Code Files

- `automesh/automesh/api/workflow.py` - API implementation
- `automesh/automesh/setup/add_dummy_workflows.py` - Dummy data script
- `automesh/automesh/setup/test_phase1_api.py` - Test suite

---

## 🎯 Next Steps

### For Backend Developers
1. ✅ Phase 1 is complete
2. 📋 Review Phase 2 features in `WORKFLOW_FEATURES_CHECKLIST.md`
3. 🚀 Start implementing Phase 2 enhancements

### For Frontend Developers
1. 📖 Read `FRONTEND_INTEGRATION_GUIDE.md`
2. 🔧 Implement API client
3. 🎨 Update UI components
4. 🧪 Test integration

### For QA/Testing
1. ✅ Run test suite (all tests passing)
2. 🔍 Manual testing with dummy data
3. 📝 Report any issues

---

## 🐛 Troubleshooting

### Issue: "No module named automesh.automesh.api.workflow"
**Solution:**
```bash
cd /home/jumes/bench-0/apps/automesh
bench --site automesh.localhost migrate
bench restart
```

### Issue: "Workflow already exists"
**Solution:** The dummy data script skips existing workflows. To recreate:
```python
# In console
import frappe
frappe.db.delete("Automesh Workflow")
frappe.db.commit()
exit()

# Then run dummy data script again
bench --site automesh.localhost execute automesh.automesh.setup.add_dummy_workflows.execute
```

### Issue: Tests failing
**Solution:**
1. Make sure dummy data is loaded
2. Check if you're logged in as Administrator
3. Verify Automesh Workflow DocType exists

### Issue: Permission denied
**Solution:** Make sure you're logged in as System Manager or Administrator

---

## 📊 Statistics

After running dummy data script:

```
Total Workflows: 8
├── Active: 6
└── Inactive: 2

Total Executions: 660 (simulated)
├── Completed: 640
└── Failed: 20

Unique Tags: 16
├── automation, ai, backup, content
├── customer, email, finance, integration
├── invoices, leads, maintenance, marketing
└── onboarding, reporting, sales, sync

Node Types Used:
├── start, end (all workflows)
├── http_request (5 workflows)
├── frappe_doc_* (7 workflows)
├── transform (3 workflows)
├── condition (2 workflows)
└── writer_generate_content (2 workflows)
```

---

## ✅ Success Checklist

- [ ] Dummy data script runs successfully
- [ ] All 7 tests pass
- [ ] Can query workflows via console
- [ ] Can filter by tags
- [ ] Can search workflows
- [ ] Can duplicate workflows
- [ ] Can toggle workflow status
- [ ] Statistics endpoint returns data
- [ ] All documentation reviewed

---

## 🎉 You're Ready!

Phase 1 is complete and production-ready. All backend APIs are:
- ✅ Implemented
- ✅ Tested (100% pass rate)
- ✅ Documented
- ✅ Ready for frontend integration

**Next:** Integrate with frontend or start Phase 2 features!

---

**Questions?** Check the documentation files or review the test suite for examples.
