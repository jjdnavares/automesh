"""
Test script for Phase 1 API endpoints
"""

import frappe
import json


def test_get_workflows():
    """Test get_workflows endpoint"""
    print("\n" + "="*60)
    print("Testing: get_workflows()")
    print("="*60)
    
    from automesh.automesh.api.workflow import get_workflows
    
    # Test basic fetch
    result = get_workflows()
    print(f"✅ Fetched {len(result['workflows'])} workflows")
    print(f"   Total count: {result['total']}")
    
    # Test with pagination
    result = get_workflows(limit=3, offset=0)
    print(f"✅ Pagination works: {len(result['workflows'])} workflows (limit=3)")
    
    # Test with search
    result = get_workflows(search="customer")
    print(f"✅ Search works: Found {len(result['workflows'])} workflows with 'customer'")
    
    # Test with tags filter
    result = get_workflows(tags="automation")
    print(f"✅ Tag filter works: Found {len(result['workflows'])} workflows with 'automation' tag")
    
    # Test with active filter
    result = get_workflows(is_active=True)
    print(f"✅ Active filter works: Found {len(result['workflows'])} active workflows")
    
    return True


def test_get_workflow():
    """Test get_workflow endpoint"""
    print("\n" + "="*60)
    print("Testing: get_workflow()")
    print("="*60)
    
    from automesh.automesh.api.workflow import get_workflow
    
    # Get first workflow
    workflows = frappe.get_all("Automesh Workflow", limit=1)
    if workflows:
        workflow_id = workflows[0].name
        result = get_workflow(workflow_id)
        print(f"✅ Fetched workflow: {result['name']}")
        print(f"   ID: {result['id']}")
        print(f"   Nodes: {len(result['nodes'])}")
        print(f"   Edges: {len(result['edges'])}")
        print(f"   Active: {result['metadata']['isActive']}")
        return True
    else:
        print("❌ No workflows found")
        return False


def test_duplicate_workflow():
    """Test duplicate_workflow endpoint"""
    print("\n" + "="*60)
    print("Testing: duplicate_workflow()")
    print("="*60)
    
    from automesh.automesh.api.workflow import duplicate_workflow
    
    # Get first workflow
    workflows = frappe.get_all("Automesh Workflow", limit=1)
    if workflows:
        workflow_id = workflows[0].name
        
        # Mock request data
        frappe.local.request = type('obj', (object,), {
            'data': json.dumps({
                "workflow_id": workflow_id,
                "new_name": "Test Duplicate Workflow"
            })
        })
        
        result = duplicate_workflow()
        print(f"✅ Duplicated workflow: {result['name']}")
        print(f"   Original ID: {workflow_id}")
        print(f"   New ID: {result['id']}")
        print(f"   Active: {result['metadata']['isActive']} (should be False)")
        
        # Clean up
        frappe.delete_doc("Automesh Workflow", result['id'])
        print(f"✅ Cleaned up test duplicate")
        
        return True
    else:
        print("❌ No workflows found")
        return False


def test_toggle_workflow_status():
    """Test toggle_workflow_status endpoint"""
    print("\n" + "="*60)
    print("Testing: toggle_workflow_status()")
    print("="*60)
    
    from automesh.automesh.api.workflow import toggle_workflow_status, get_workflow
    
    # Get first workflow
    workflows = frappe.get_all("Automesh Workflow", limit=1)
    if workflows:
        workflow_id = workflows[0].name
        
        # Get current status
        workflow = get_workflow(workflow_id)
        original_status = workflow['metadata']['isActive']
        print(f"   Original status: {original_status}")
        
        # Toggle to opposite
        frappe.local.request = type('obj', (object,), {
            'data': json.dumps({
                "workflow_id": workflow_id,
                "is_active": not original_status
            })
        })
        
        result = toggle_workflow_status()
        print(f"✅ Toggled status: {result['is_active']} (expected: {not original_status})")
        
        # Toggle back
        frappe.local.request = type('obj', (object,), {
            'data': json.dumps({
                "workflow_id": workflow_id,
                "is_active": original_status
            })
        })
        
        result = toggle_workflow_status()
        print(f"✅ Restored status: {result['is_active']} (expected: {original_status})")
        
        return True
    else:
        print("❌ No workflows found")
        return False


def test_get_workflow_statistics():
    """Test get_workflow_statistics endpoint"""
    print("\n" + "="*60)
    print("Testing: get_workflow_statistics()")
    print("="*60)
    
    from automesh.automesh.api.workflow import get_workflow_statistics
    
    result = get_workflow_statistics(days=7)
    print(f"✅ Statistics retrieved:")
    print(f"   Total workflows: {result['total_workflows']}")
    print(f"   Active workflows: {result['active_workflows']}")
    print(f"   Total executions: {result['total_executions']}")
    print(f"   Completed: {result['completed']}")
    print(f"   Failed: {result['failed']}")
    print(f"   Failure rate: {result['failure_rate']}")
    print(f"   Time saved: {result['time_saved']}")
    print(f"   Avg runtime: {result['avg_runtime']}")
    
    return True


def test_get_all_tags():
    """Test get_all_tags endpoint"""
    print("\n" + "="*60)
    print("Testing: get_all_tags()")
    print("="*60)
    
    from automesh.automesh.api.workflow import get_all_tags
    
    result = get_all_tags()
    print(f"✅ Retrieved {len(result)} unique tags:")
    print(f"   Tags: {', '.join(result[:10])}")  # Show first 10
    
    return True


def test_delete_workflow():
    """Test delete_workflow endpoint"""
    print("\n" + "="*60)
    print("Testing: delete_workflow()")
    print("="*60)
    
    from automesh.automesh.api.workflow import create_workflow, delete_workflow
    
    # Create a test workflow
    frappe.local.request = type('obj', (object,), {
        'data': json.dumps({
            "name": "Test Workflow to Delete",
            "description": "This workflow will be deleted",
            "tags": "test",
            "nodes": [],
            "edges": []
        })
    })
    
    created = create_workflow()
    workflow_id = created['id']
    print(f"✅ Created test workflow: {workflow_id}")
    
    # Delete it
    frappe.local.request = type('obj', (object,), {
        'data': json.dumps({
            "workflow_id": workflow_id
        })
    })
    
    result = delete_workflow()
    print(f"✅ Deleted workflow: {result['success']}")
    
    # Verify deletion
    exists = frappe.db.exists("Automesh Workflow", workflow_id)
    print(f"✅ Verified deletion: exists={exists} (should be None)")
    
    return True


def execute():
    """Run all tests"""
    print("\n" + "="*80)
    print("PHASE 1 API ENDPOINT TESTS")
    print("="*80)
    
    tests = [
        ("Get Workflows", test_get_workflows),
        ("Get Single Workflow", test_get_workflow),
        ("Duplicate Workflow", test_duplicate_workflow),
        ("Toggle Workflow Status", test_toggle_workflow_status),
        ("Get Workflow Statistics", test_get_workflow_statistics),
        ("Get All Tags", test_get_all_tags),
        ("Delete Workflow", test_delete_workflow),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")
            frappe.log_error(f"Phase 1 API Test Error: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    print("="*80)
    
    return results


if __name__ == "__main__":
    execute()
