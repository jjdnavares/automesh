# Phase 2 Installation & Setup Guide

**AutoMesh Workflow Management - Phase 2**  
**Date:** 2025-10-03

---

## 📋 Prerequisites

- Frappe bench installed and configured
- AutoMesh app already installed
- Phase 1 features working correctly
- Access to bench commands

---

## 🚀 Installation Steps

### Step 1: Install the New DocType

The new `Automesh Workflow Share` DocType needs to be installed in your Frappe site.

```bash
cd /home/jumes/bench-0

# Run migrations to install the new DocType
bench --site [your-site-name] migrate

# Example:
# bench --site site1.local migrate
```

**Expected Output:**
```
Migrating site1.local
Executing automesh.patches.v1_0.install_workflow_share_doctype
Installing Automesh Workflow Share
Migration complete
```

---

### Step 2: Verify DocType Installation

```bash
# Check if DocType exists
bench --site [your-site-name] console

# In the console:
>>> frappe.db.exists("DocType", "Automesh Workflow Share")
'Automesh Workflow Share'

>>> exit()
```

---

### Step 3: Run Tests (Optional but Recommended)

```bash
# Run all AutoMesh tests
bench --site [your-site-name] run-tests --app automesh

# Run specific DocType tests
bench --site [your-site-name] run-tests --app automesh --doctype "Automesh Workflow Share"
```

---

### Step 4: Verify API Endpoints

Test that the new API endpoints are accessible:

```bash
# Using curl or your API client
curl -X POST http://localhost:8000/api/method/automesh.automesh.api.workflow.share_workflow \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "test-workflow",
    "shared_with": "user@example.com",
    "permission_level": "view"
  }'
```

---

### Step 5: Clear Cache

```bash
# Clear bench cache
bench --site [your-site-name] clear-cache

# Restart bench
bench restart
```

---

## ✅ Verification Checklist

After installation, verify the following:

### Backend Verification

- [ ] DocType `Automesh Workflow Share` exists in DocType list
- [ ] Can create a workflow share record manually
- [ ] API endpoint `share_workflow` is accessible
- [ ] API endpoint `get_workflow_shares` is accessible
- [ ] API endpoint `revoke_workflow_share` is accessible
- [ ] API endpoint `update_workflow_share` is accessible

### Frontend Verification

- [ ] Workflow list page loads without errors
- [ ] Bulk selection checkboxes appear
- [ ] Bulk actions toolbar works
- [ ] Quick execute button works
- [ ] Templates button opens dialog
- [ ] Import/Export buttons work
- [ ] Statistics display correctly

---

## 🧪 Testing the Sharing Feature

### Test 1: Share a Workflow

```python
# In Frappe console
import frappe

# Create a test workflow
workflow = frappe.get_doc({
    "doctype": "Automesh Workflow",
    "title": "Test Workflow for Sharing",
    "description": "Test",
    "version": "1.0.0",
    "is_active": 1,
    "created_by": "Administrator"
})
workflow.insert()

# Share the workflow
share = frappe.get_doc({
    "doctype": "Automesh Workflow Share",
    "workflow": "Test Workflow for Sharing",
    "shared_with": "user@example.com",
    "permission_level": "view",
    "shared_by": "Administrator",
    "is_active": 1
})
share.insert()

print(f"Share created: {share.name}")
```

### Test 2: Check Permissions

```python
# Check if user can access workflow
from automesh.automesh.api.workflow import _can_access_workflow

frappe.set_user("user@example.com")
can_access = _can_access_workflow("Test Workflow for Sharing")
print(f"User can access: {can_access}")  # Should be True
```

### Test 3: Revoke Share

```python
# Revoke the share
share = frappe.get_doc("Automesh Workflow Share", "AMWFS-00001")
share.is_active = 0
share.save()

# Check access again
can_access = _can_access_workflow("Test Workflow for Sharing")
print(f"User can access: {can_access}")  # Should be False
```

---

## 🔧 Troubleshooting

### Issue: DocType Not Found

**Error:** `DocType Automesh Workflow Share not found`

**Solution:**
```bash
# Force reload the DocType
bench --site [your-site-name] reload-doctype "Automesh Workflow Share"

# Or reinstall the app
bench --site [your-site-name] reinstall-app automesh
```

### Issue: API Endpoints Not Working

**Error:** `404 Not Found` or `Method not found`

**Solution:**
```bash
# Clear cache and restart
bench --site [your-site-name] clear-cache
bench restart

# Check if API file is correct
cat automesh/automesh/api/workflow.py | grep "share_workflow"
```

### Issue: Permission Denied

**Error:** `You don't have permission to share this workflow`

**Solution:**
- Ensure user is the workflow owner or has System Manager role
- Check if `_can_access_workflow()` is working correctly
- Verify user has proper Frappe permissions

### Issue: Duplicate Share Error

**Error:** `This workflow is already shared with this user`

**Solution:**
- This is expected behavior - update the existing share instead
- Or revoke the old share first, then create a new one

---

## 📊 Database Schema

The new DocType creates the following table:

```sql
-- Table: tabAutomesh Workflow Share
CREATE TABLE `tabAutomesh Workflow Share` (
  `name` varchar(140) NOT NULL,
  `workflow` varchar(140) DEFAULT NULL,
  `shared_with` varchar(140) DEFAULT NULL,
  `permission_level` varchar(140) DEFAULT NULL,
  `shared_by` varchar(140) DEFAULT NULL,
  `shared_at` datetime(6) DEFAULT NULL,
  `expires_at` datetime(6) DEFAULT NULL,
  `is_active` int(1) DEFAULT 1,
  `creation` datetime(6) DEFAULT NULL,
  `modified` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`name`),
  KEY `workflow` (`workflow`),
  KEY `shared_with` (`shared_with`),
  KEY `is_active` (`is_active`)
);
```

---

## 🎯 Next Steps After Installation

### 1. Create Sample Shares (Optional)

```python
# Create some test shares for development
shares_data = [
    {
        "workflow": "My Workflow",
        "shared_with": "user1@example.com",
        "permission_level": "view"
    },
    {
        "workflow": "My Workflow",
        "shared_with": "user2@example.com",
        "permission_level": "edit"
    }
]

for data in shares_data:
    share = frappe.get_doc({
        "doctype": "Automesh Workflow Share",
        **data,
        "shared_by": frappe.session.user,
        "is_active": 1
    })
    share.insert()
```

### 2. Add UI Components (Future)

The backend is complete. To add UI:
1. Create share dialog component
2. Add user picker with autocomplete
3. Display current shares in workflow detail page
4. Add share button to workflow cards

### 3. Set Up Notifications (Future)

```python
# Send email when workflow is shared
def on_share_created(doc, method):
    frappe.sendmail(
        recipients=[doc.shared_with],
        subject=f"Workflow Shared: {doc.workflow}",
        message=f"{doc.shared_by} shared a workflow with you"
    )

# Add to hooks.py
doc_events = {
    "Automesh Workflow Share": {
        "after_insert": "automesh.utils.on_share_created"
    }
}
```

---

## 📚 API Usage Examples

### Share Workflow (JavaScript)

```javascript
// Share with view permission
frappe.call({
    method: 'automesh.automesh.api.workflow.share_workflow',
    args: {
        workflow_id: 'my-workflow',
        shared_with: 'user@example.com',
        permission_level: 'view'
    },
    callback: function(r) {
        console.log('Share created:', r.message.share_id);
    }
});
```

### Get Shares (JavaScript)

```javascript
// Get all shares for a workflow
frappe.call({
    method: 'automesh.automesh.api.workflow.get_workflow_shares',
    args: {
        workflow_id: 'my-workflow'
    },
    callback: function(r) {
        console.log('Shares:', r.message);
    }
});
```

### Revoke Share (JavaScript)

```javascript
// Revoke a share
frappe.call({
    method: 'automesh.automesh.api.workflow.revoke_workflow_share',
    args: {
        share_id: 'AMWFS-00001'
    },
    callback: function(r) {
        console.log('Share revoked');
    }
});
```

---

## 🔐 Security Considerations

### Permission Levels Explained

- **view**: Read-only access to workflow
- **execute**: Can run the workflow
- **edit**: Can modify workflow nodes/edges
- **full**: Complete control (can share, delete)

### Best Practices

1. **Principle of Least Privilege**: Give users minimum required permissions
2. **Expiration Dates**: Set expiration for temporary access
3. **Regular Audits**: Review shares periodically
4. **Owner Control**: Only owners/admins can share workflows
5. **Revoke Promptly**: Remove access when no longer needed

---

## 📞 Support

If you encounter issues:

1. Check the logs: `bench --site [site] logs`
2. Review error messages in browser console
3. Verify DocType installation: `bench console`
4. Run tests: `bench run-tests --app automesh`
5. Check documentation: `PHASE2_COMPLETE.md`

---

**Installation Guide Version:** 1.0  
**Last Updated:** 2025-10-03  
**Tested On:** Frappe v14+
