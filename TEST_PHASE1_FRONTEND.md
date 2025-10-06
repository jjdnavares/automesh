# Phase 1 Frontend Testing Guide

**Date:** 2025-10-02
**Purpose:** Verify all Phase 1 frontend implementations are working correctly

---

## Prerequisites

1. **Backend Running**: Ensure Frappe/AutoMesh backend is running
2. **Frontend Running**: Ensure React frontend is running
3. **Sample Data**: Backend should have sample workflows (created in Phase 1 backend testing)

---

## Test Environment Setup

### Start Backend (if not running)
```bash
cd /home/jumes/bench-0
bench start
```

### Start Frontend (if not running)
```bash
cd /home/jumes/bench-0/apps/automesh/frontend
npm run dev
# or
yarn dev
```

### Access Application
- Frontend: http://localhost:5173 (or configured port)
- Backend API: http://localhost:8000

---

## Test Cases

### Test 1: Initial Page Load ✅

**Objective**: Verify workflow list loads correctly

**Steps**:
1. Navigate to workflow list page
2. Observe loading state
3. Wait for workflows to load

**Expected Results**:
- ✅ Loading spinner appears initially
- ✅ Workflows load and display in cards
- ✅ Statistics section shows data (executions, failure rate, time saved)
- ✅ No console errors

**API Call**: `GET /api/method/automesh.automesh.api.workflow.get_workflows`

---

### Test 2: Search Functionality ✅

**Objective**: Verify search filters workflows correctly

**Steps**:
1. Type in search box: "Content"
2. Wait 300ms (debounce)
3. Observe filtered results

**Expected Results**:
- ✅ Search input accepts text
- ✅ Results filter after debounce delay
- ✅ Only matching workflows shown
- ✅ Clear search shows all workflows again

**API Call**: `GET /api/method/automesh.automesh.api.workflow.get_workflows?search=Content`

---

### Test 3: Status Filter ✅

**Objective**: Verify status filtering works

**Steps**:
1. Click status filter dropdown
2. Select "Active"
3. Observe results
4. Select "Inactive"
5. Observe results
6. Select "All statuses"

**Expected Results**:
- ✅ Dropdown opens and shows options
- ✅ "Active" shows only active workflows
- ✅ "Inactive" shows only inactive workflows
- ✅ "All statuses" shows all workflows

**API Calls**: 
- `GET /api/method/automesh.automesh.api.workflow.get_workflows?is_active=1`
- `GET /api/method/automesh.automesh.api.workflow.get_workflows?is_active=0`

---

### Test 4: Sorting ✅

**Objective**: Verify sorting works correctly

**Steps**:
1. Click sort dropdown
2. Select "Name"
3. Observe order
4. Click sort order button (asc/desc)
5. Observe order changes
6. Try other sort options

**Expected Results**:
- ✅ Workflows sort by selected field
- ✅ Sort order toggles correctly
- ✅ Icon changes between asc/desc

**API Call**: `GET /api/method/automesh.automesh.api.workflow.get_workflows?sort_by=title&sort_order=asc`

---

### Test 5: Create Workflow ✅

**Objective**: Verify workflow creation works

**Steps**:
1. Click "Create Workflow" button
2. Enter name: "Test Workflow"
3. Enter description: "Test Description"
4. Click "Create Workflow"
5. Observe navigation

**Expected Results**:
- ✅ Create form appears
- ✅ Form accepts input
- ✅ Submit button disabled until name entered
- ✅ Success toast appears
- ✅ Navigates to workflow editor
- ✅ New workflow appears in list

**API Call**: `POST /api/method/automesh.automesh.api.workflow.create_workflow`

---

### Test 6: Delete Workflow ✅

**Objective**: Verify workflow deletion with confirmation

**Steps**:
1. Click trash icon on a workflow
2. Observe confirmation dialog
3. Click "Cancel"
4. Observe dialog closes
5. Click trash icon again
6. Click "Delete"
7. Observe workflow removed

**Expected Results**:
- ✅ Confirmation dialog appears
- ✅ Cancel closes dialog without deleting
- ✅ Delete removes workflow
- ✅ Success toast appears
- ✅ List refreshes automatically
- ✅ Workflow no longer in list

**API Call**: `POST /api/method/automesh.automesh.api.workflow.delete_workflow`

---

### Test 7: Duplicate Workflow ✅

**Objective**: Verify workflow duplication

**Steps**:
1. Click copy icon on a workflow
2. Observe loading state on button
3. Wait for completion
4. Observe navigation

**Expected Results**:
- ✅ Button shows loading spinner
- ✅ Success toast appears
- ✅ Navigates to duplicated workflow editor
- ✅ New workflow has "(Copy)" appended to name
- ✅ New workflow appears in list

**API Call**: `POST /api/method/automesh.automesh.api.workflow.duplicate_workflow`

---

### Test 8: Toggle Workflow Status ✅

**Objective**: Verify status toggle works

**Steps**:
1. Note current status badge (Active/Inactive)
2. Click on the badge
3. Observe loading state
4. Observe status change

**Expected Results**:
- ✅ Badge is clickable
- ✅ Loading spinner appears in badge
- ✅ Status toggles (Active ↔ Inactive)
- ✅ Success toast appears
- ✅ Badge color changes
- ✅ List refreshes

**API Call**: `POST /api/method/automesh.automesh.api.workflow.toggle_workflow_status`

---

### Test 9: Statistics Loading ✅

**Objective**: Verify statistics load correctly

**Steps**:
1. Refresh page
2. Observe statistics section
3. Check values

**Expected Results**:
- ✅ Loading spinner shows initially
- ✅ Statistics load and display
- ✅ Shows: Total executions, Failure rate, Time saved
- ✅ Values are realistic (not placeholder)

**API Call**: `GET /api/method/automesh.automesh.api.workflow.get_workflow_statistics?days=7`

---

### Test 10: Error Handling ✅

**Objective**: Verify error states work correctly

**Steps**:
1. Stop backend server
2. Refresh page
3. Observe error state
4. Click "Retry" button
5. Start backend server
6. Observe recovery

**Expected Results**:
- ✅ Error message displays
- ✅ Error is user-friendly
- ✅ Retry button appears
- ✅ Retry button works when backend restored
- ✅ Error toast appears for failed operations

---

### Test 11: Empty State ✅

**Objective**: Verify empty state displays correctly

**Steps**:
1. Delete all workflows (or use fresh database)
2. Navigate to workflow list
3. Observe empty state

**Expected Results**:
- ✅ Empty state message displays
- ✅ "Create workflow" button appears
- ✅ Clicking button opens create form
- ✅ No errors in console

---

### Test 12: Loading States ✅

**Objective**: Verify all loading indicators work

**Steps**:
1. Perform each operation (create, delete, duplicate, toggle)
2. Observe loading states

**Expected Results**:
- ✅ Initial page load shows spinner
- ✅ Statistics section shows spinner
- ✅ Action buttons show spinner during operation
- ✅ Buttons disabled during operation
- ✅ Badge shows spinner during toggle

---

## Browser Console Tests

### Check for Errors
Open browser console (F12) and verify:
- ✅ No red errors
- ✅ No unhandled promise rejections
- ✅ API calls succeed (check Network tab)

### Check API Responses
In Network tab, verify:
- ✅ All API calls return 200 status
- ✅ Response format matches expected structure
- ✅ Pagination metadata included in responses

---

## Performance Tests

### Test 13: Search Debouncing ✅

**Objective**: Verify search is debounced

**Steps**:
1. Open Network tab
2. Type quickly in search: "test"
3. Count API calls

**Expected Results**:
- ✅ Only 1 API call made (after 300ms delay)
- ✅ Not 4 calls (one per character)

---

### Test 14: State Management ✅

**Objective**: Verify state updates correctly

**Steps**:
1. Load workflows
2. Filter by active
3. Create new workflow
4. Return to list
5. Verify new workflow appears

**Expected Results**:
- ✅ State persists during navigation
- ✅ New workflow appears in list
- ✅ Filters remain applied

---

## Integration Tests

### Test 15: Full Workflow CRUD Cycle ✅

**Objective**: Test complete lifecycle

**Steps**:
1. Create workflow "Integration Test"
2. Navigate back to list
3. Search for "Integration"
4. Duplicate the workflow
5. Navigate back to list
6. Toggle status on original
7. Delete duplicate
8. Delete original

**Expected Results**:
- ✅ All operations succeed
- ✅ Toasts appear for each action
- ✅ List updates correctly
- ✅ No errors in console

---

## Accessibility Tests

### Test 16: Keyboard Navigation ✅

**Objective**: Verify keyboard accessibility

**Steps**:
1. Use Tab key to navigate
2. Use Enter to activate buttons
3. Use Escape to close dialogs

**Expected Results**:
- ✅ All interactive elements focusable
- ✅ Focus indicators visible
- ✅ Keyboard shortcuts work

---

## Mobile Responsiveness

### Test 17: Mobile View ✅

**Objective**: Verify mobile layout

**Steps**:
1. Open DevTools
2. Toggle device toolbar
3. Select mobile device
4. Test all features

**Expected Results**:
- ✅ Layout adapts to mobile
- ✅ All features accessible
- ✅ Touch targets adequate size
- ✅ No horizontal scroll

---

## Test Results Summary

| Test # | Test Name | Status | Notes |
|--------|-----------|--------|-------|
| 1 | Initial Page Load | ⏳ Pending | |
| 2 | Search Functionality | ⏳ Pending | |
| 3 | Status Filter | ⏳ Pending | |
| 4 | Sorting | ⏳ Pending | |
| 5 | Create Workflow | ⏳ Pending | |
| 6 | Delete Workflow | ⏳ Pending | |
| 7 | Duplicate Workflow | ⏳ Pending | |
| 8 | Toggle Status | ⏳ Pending | |
| 9 | Statistics Loading | ⏳ Pending | |
| 10 | Error Handling | ⏳ Pending | |
| 11 | Empty State | ⏳ Pending | |
| 12 | Loading States | ⏳ Pending | |
| 13 | Search Debouncing | ⏳ Pending | |
| 14 | State Management | ⏳ Pending | |
| 15 | Full CRUD Cycle | ⏳ Pending | |
| 16 | Keyboard Navigation | ⏳ Pending | |
| 17 | Mobile View | ⏳ Pending | |

---

## Known Issues to Check

1. **Pagination**: UI not yet implemented (API ready)
2. **Tags**: Filter UI not yet implemented (API ready)
3. **Optimistic Updates**: Some operations refresh entire list

---

## Automated Testing Script

Create a test file to automate API testing:

```javascript
// test-phase1-api.js
const BASE_URL = 'http://localhost:8000';

async function testAPI() {
  console.log('🧪 Testing Phase 1 Frontend APIs...\n');
  
  // Test 1: Get Workflows
  console.log('Test 1: Get Workflows');
  const workflows = await fetch(`${BASE_URL}/api/method/automesh.automesh.api.workflow.get_workflows`);
  console.log('✅ Status:', workflows.status);
  
  // Test 2: Get Workflows with Search
  console.log('\nTest 2: Get Workflows with Search');
  const searchResult = await fetch(`${BASE_URL}/api/method/automesh.automesh.api.workflow.get_workflows?search=test`);
  console.log('✅ Status:', searchResult.status);
  
  // Test 3: Get Statistics
  console.log('\nTest 3: Get Statistics');
  const stats = await fetch(`${BASE_URL}/api/method/automesh.automesh.api.workflow.get_workflow_statistics?days=7`);
  console.log('✅ Status:', stats.status);
  
  console.log('\n✅ All API tests passed!');
}

testAPI().catch(console.error);
```

Run with: `node test-phase1-api.js`

---

## Conclusion

Complete all tests above and mark them as ✅ Pass or ❌ Fail in the summary table. Document any issues found for Phase 2 improvements.

**Testing Duration**: ~30-45 minutes
**Required**: Manual testing (automated tests optional)
**Priority**: High (before Phase 2)

---

**Created by**: AI Assistant
**Date**: 2025-10-02
**Version**: 1.0.0
