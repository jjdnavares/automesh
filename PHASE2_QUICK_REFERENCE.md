# Phase 2 Quick Reference Guide

**AutoMesh Workflow Management - Phase 2 Features**  
**Last Updated:** 2025-10-03

---

## 🚀 Quick Start

### Using Bulk Operations

1. **Select Workflows:**
   - Click checkbox on any workflow card
   - Or click "Select All" button above the list

2. **Perform Bulk Actions:**
   - **Activate All** - Activate all selected workflows
   - **Deactivate All** - Deactivate all selected workflows
   - **Delete All** - Delete all selected workflows (with confirmation)

3. **Clear Selection:**
   - Click "Clear Selection" in the bulk actions toolbar
   - Or click "Select All" again to deselect all

---

### Quick Execute Workflow

**From Workflow List:**
1. Click the **Play button (▶️)** on any workflow card
2. Workflow executes immediately with default inputs
3. Toast notification shows execution ID

**Use Case:** Quick testing or running workflows without opening the editor

---

### Using Templates

1. **Browse Templates:**
   - Click **"Templates"** button in the header
   - Browse available templates in the dialog

2. **Create from Template:**
   - Click on any template card
   - Workflow is created automatically
   - Redirected to the new workflow editor

**Template Naming:** `[Template Name] - [Date]`

---

### Import/Export Workflows

**Export Workflow:**
1. Click the **Download icon (⬇️)** on any workflow card
2. JSON file downloads automatically
3. Filename: `workflow-[name].json`

**Import Workflow:**
1. Click **"Import"** button in the header
2. Select a workflow JSON file
3. Workflow is imported and opened automatically

**Export Format:**
```json
{
  "title": "Workflow Name",
  "description": "Description",
  "version": "1.0.0",
  "tags": "tag1,tag2",
  "workflow_json": "{...}",
  "exported_at": "2025-10-03T05:00:00",
  "exported_by": "user@example.com"
}
```

---

### View Statistics

**Location:** Top of workflow list page

**Metrics Displayed:**
- **Total Executions** - Last 7 days
- **Failure Rate** - Percentage of failed executions
- **Time Saved** - Estimated time saved (5 min per execution)

**Refresh:** Statistics refresh automatically when page loads

---

## 🎯 Feature Matrix

| Feature | Status | Location | Action |
|---------|--------|----------|--------|
| Bulk Delete | ✅ | Workflow List | Select workflows → Delete All |
| Bulk Activate | ✅ | Workflow List | Select workflows → Activate All |
| Bulk Deactivate | ✅ | Workflow List | Select workflows → Deactivate All |
| Quick Execute | ✅ | Workflow Card | Click Play button |
| Export Workflow | ✅ | Workflow Card | Click Download icon |
| Import Workflow | ✅ | Page Header | Click Import button |
| Templates | ✅ | Page Header | Click Templates button |
| Statistics | ✅ | Page Top | Auto-displayed |
| Execution History | ⏳ | API Ready | UI pending |
| Tags Filtering | ⏳ | API Ready | Enhanced UI pending |

---

## 📱 UI Components

### Workflow Card Actions

```
┌─────────────────────────────────────────────────┐
│ ☐ Workflow Name                    [Active] ▶️ ✏️ 📋 ⬇️ 🗑️ │
│ Description text here...                        │
│                                                 │
│ Last updated: 10/03/2025  Executions: 42       │
└─────────────────────────────────────────────────┘
```

**Icons:**
- ☐ - Selection checkbox
- ▶️ - Quick execute
- ✏️ - Edit workflow
- 📋 - Duplicate workflow
- ⬇️ - Export workflow
- 🗑️ - Delete workflow

### Bulk Actions Toolbar

```
┌─────────────────────────────────────────────────┐
│ 3 workflow(s) selected  [Clear Selection]      │
│                                                 │
│ [Activate All] [Deactivate All] [Delete All]   │
└─────────────────────────────────────────────────┘
```

**Appears when:** One or more workflows selected

---

## 🔧 API Endpoints

### Bulk Operations

**Bulk Delete:**
```
POST /api/method/automesh.automesh.api.workflow.bulk_delete_workflows
Body: { "workflow_ids": ["id1", "id2"] }
```

**Bulk Update Status:**
```
POST /api/method/automesh.automesh.api.workflow.bulk_update_status
Body: { "workflow_ids": ["id1", "id2"], "is_active": true }
```

### Templates

**Get Templates:**
```
GET /api/method/automesh.automesh.api.workflow.get_templates?category=automation
```

**Create from Template:**
```
POST /api/method/automesh.automesh.api.workflow.create_workflow_from_template
Body: { "template_id": "template-1", "workflow_name": "My Workflow" }
```

### Import/Export

**Export:**
```
POST /api/method/automesh.automesh.api.workflow.export_workflow_json
Body: { "workflow_id": "workflow-1" }
```

**Import:**
```
POST /api/method/automesh.automesh.api.workflow.import_workflow_json
Body: { "import_data": { ... } }
```

### Execution History

**Get Executions:**
```
GET /api/method/automesh.automesh.api.workflow.get_workflow_executions
Params: workflow_id, limit=10, offset=0, status=completed
```

---

## 💡 Tips & Best Practices

### Bulk Operations
- ✅ Use bulk activate/deactivate for seasonal workflows
- ✅ Select All for quick operations on filtered results
- ⚠️ Bulk delete is permanent - use with caution
- ✅ Failed operations are reported in toast notifications

### Quick Execute
- ✅ Perfect for testing workflows
- ✅ Uses default/empty input data
- ⚠️ For custom inputs, use the workflow editor
- ✅ Execution ID shown in toast for tracking

### Templates
- ✅ Create templates for common workflow patterns
- ✅ Templates can include pre-configured nodes
- ✅ Customize after creation
- ✅ Share templates via export/import

### Import/Export
- ✅ Export workflows for backup
- ✅ Share workflows between environments
- ✅ Version control workflows in Git
- ⚠️ Imported workflows get "(Imported)" suffix
- ✅ JSON format is human-readable

---

## 🐛 Troubleshooting

### Bulk Operations Not Working
**Issue:** Bulk actions fail silently  
**Solution:** Check permissions - you need admin/owner rights

### Import Fails
**Issue:** "Invalid workflow data" error  
**Solution:** Ensure JSON has required fields: `title`, `workflow_json`

### Quick Execute Not Starting
**Issue:** Workflow doesn't execute  
**Solution:** Check workflow has valid start node and is properly configured

### Templates Not Loading
**Issue:** Empty templates dialog  
**Solution:** Create templates in Automesh Template DocType first

---

## 📊 Keyboard Shortcuts (Future)

*Planned for Phase 3*

- `Ctrl/Cmd + A` - Select all workflows
- `Ctrl/Cmd + E` - Export selected
- `Ctrl/Cmd + I` - Import workflow
- `Delete` - Delete selected workflows

---

## 🔗 Related Documentation

- **Phase 2 Complete:** `PHASE2_IMPLEMENTATION_COMPLETE.md`
- **API Reference:** `API_QUICK_REFERENCE.md`
- **Feature Checklist:** `WORKFLOW_FEATURES_CHECKLIST.md`
- **Phase 1 Guide:** `README_PHASE1.md`

---

## 📞 Support

For issues or questions:
1. Check `WORKFLOW_FEATURES_CHECKLIST.md` for feature status
2. Review `PHASE2_IMPLEMENTATION_COMPLETE.md` for implementation details
3. Test with sample workflows first
4. Check browser console for errors

---

**Version:** Phase 2.0  
**Last Updated:** 2025-10-03  
**Status:** 7/8 Features Complete (87.5%)
