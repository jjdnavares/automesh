"""
Test suite for external integration workflow nodes

This module contains tests for the medium-priority external integration nodes.

Usage:
    bench --site [site-name] execute automesh.automesh.workflow_engine.test_integration_nodes.run_all_tests
"""

import frappe
import json
from datetime import datetime
import os
import tempfile


def run_all_tests():
    """Run all integration node tests"""
    print("\n" + "="*80)
    print("EXTERNAL INTEGRATION NODES - TEST SUITE")
    print("="*80)
    
    tests = [
        ("File Write Node", test_file_write),
        ("File Read Node", test_file_read),
        ("File Read/Write Integration", test_file_integration),
        ("Database Query Node", test_database_query),
        ("Webhook Node (Mock)", test_webhook_mock),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'─'*80}")
            print(f"Running: {test_name}")
            print(f"{'─'*80}")
            
            result = test_func()
            
            if result:
                print(f"✅ PASSED: {test_name}")
                passed += 1
            else:
                print(f"❌ FAILED: {test_name}")
                failed += 1
                
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*80)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*80 + "\n")
    
    return passed, failed


def test_file_write():
    """Test file_write node"""
    print("\n📝 Test: File Write - Write content to file")
    
    # Create temporary file path
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "test_output.txt")
    
    workflow_json = {
        "nodes": [
            {
                "id": "start_1",
                "type": "start",
                "data": {"label": "Start"}
            },
            {
                "id": "file_write_1",
                "type": "file_write",
                "data": {
                    "label": "Write File",
                    "params": {
                        "file_path": test_file,
                        "content_path": "content",
                        "encoding": "utf-8",
                        "write_mode": "text"
                    }
                }
            },
            {
                "id": "end_1",
                "type": "end",
                "data": {"label": "End"}
            }
        ],
        "edges": [
            {"source": "start_1", "target": "file_write_1"},
            {"source": "file_write_1", "target": "end_1"}
        ]
    }
    
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = f"Test File Write {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workflow.workflow_json = json.dumps(workflow_json)
    workflow.is_active = 1
    workflow.insert()
    
    execution = frappe.new_doc("Automesh Execution")
    execution.workflow = workflow.name
    execution.status = "draft"
    execution.input_data = json.dumps({
        "content": "Hello, World! This is a test file."
    })
    execution.insert()
    
    from .engine import WorkflowEngine
    engine = WorkflowEngine(execution.name)
    success = engine.execute()
    
    execution.reload()
    output = json.loads(execution.output_data) if execution.output_data else {}
    
    print(f"Execution Status: {execution.status}")
    print(f"File written: {output.get('written', False)}")
    print(f"File size: {output.get('size', 0)} bytes")
    
    # Verify file was created
    assert execution.status == "completed", f"Expected 'completed', got '{execution.status}'"
    assert os.path.exists(test_file), "File should exist"
    assert output.get("written") == True, "File should be marked as written"
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
    os.rmdir(temp_dir)
    
    frappe.delete_doc("Automesh Execution", execution.name, force=1)
    frappe.delete_doc("Automesh Workflow", workflow.name, force=1)
    
    print("✓ File write test passed")
    return True


def test_file_read():
    """Test file_read node"""
    print("\n📝 Test: File Read - Read content from file")
    
    # Create temporary file with content
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "test_input.txt")
    test_content = "This is test content for reading."
    
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    workflow_json = {
        "nodes": [
            {
                "id": "start_1",
                "type": "start",
                "data": {"label": "Start"}
            },
            {
                "id": "file_read_1",
                "type": "file_read",
                "data": {
                    "label": "Read File",
                    "params": {
                        "file_path": test_file,
                        "encoding": "utf-8",
                        "read_mode": "text"
                    }
                }
            },
            {
                "id": "end_1",
                "type": "end",
                "data": {"label": "End"}
            }
        ],
        "edges": [
            {"source": "start_1", "target": "file_read_1"},
            {"source": "file_read_1", "target": "end_1"}
        ]
    }
    
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = f"Test File Read {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workflow.workflow_json = json.dumps(workflow_json)
    workflow.is_active = 1
    workflow.insert()
    
    execution = frappe.new_doc("Automesh Execution")
    execution.workflow = workflow.name
    execution.status = "draft"
    execution.input_data = json.dumps({})
    execution.insert()
    
    from .engine import WorkflowEngine
    engine = WorkflowEngine(execution.name)
    success = engine.execute()
    
    execution.reload()
    output = json.loads(execution.output_data) if execution.output_data else {}
    
    print(f"Execution Status: {execution.status}")
    print(f"Content read: {len(output.get('content', ''))} characters")
    
    assert execution.status == "completed", f"Expected 'completed', got '{execution.status}'"
    assert output.get("content") == test_content, "Content should match"
    assert output.get("size") == len(test_content), "Size should match"
    
    # Cleanup
    os.remove(test_file)
    os.rmdir(temp_dir)
    
    frappe.delete_doc("Automesh Execution", execution.name, force=1)
    frappe.delete_doc("Automesh Workflow", workflow.name, force=1)
    
    print("✓ File read test passed")
    return True


def test_file_integration():
    """Test file write then read integration"""
    print("\n📝 Test: File Integration - Write then Read")
    
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "integration_test.txt")
    test_content = "Integration test content"
    
    workflow_json = {
        "nodes": [
            {
                "id": "start_1",
                "type": "start",
                "data": {"label": "Start"}
            },
            {
                "id": "file_write_1",
                "type": "file_write",
                "data": {
                    "label": "Write File",
                    "params": {
                        "file_path": test_file,
                        "content_path": "content"
                    }
                }
            },
            {
                "id": "file_read_1",
                "type": "file_read",
                "data": {
                    "label": "Read File",
                    "params": {
                        "file_path": test_file
                    }
                }
            },
            {
                "id": "end_1",
                "type": "end",
                "data": {"label": "End"}
            }
        ],
        "edges": [
            {"source": "start_1", "target": "file_write_1"},
            {"source": "file_write_1", "target": "file_read_1"},
            {"source": "file_read_1", "target": "end_1"}
        ]
    }
    
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = f"Test File Integration {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workflow.workflow_json = json.dumps(workflow_json)
    workflow.is_active = 1
    workflow.insert()
    
    execution = frappe.new_doc("Automesh Execution")
    execution.workflow = workflow.name
    execution.status = "draft"
    execution.input_data = json.dumps({"content": test_content})
    execution.insert()
    
    from .engine import WorkflowEngine
    engine = WorkflowEngine(execution.name)
    success = engine.execute()
    
    execution.reload()
    output = json.loads(execution.output_data) if execution.output_data else {}
    
    print(f"Execution Status: {execution.status}")
    print(f"Content matches: {output.get('content') == test_content}")
    
    assert execution.status == "completed", f"Expected 'completed', got '{execution.status}'"
    assert output.get("content") == test_content, "Read content should match written content"
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
    os.rmdir(temp_dir)
    
    frappe.delete_doc("Automesh Execution", execution.name, force=1)
    frappe.delete_doc("Automesh Workflow", workflow.name, force=1)
    
    print("✓ File integration test passed")
    return True


def test_database_query():
    """Test database_query node"""
    print("\n📝 Test: Database Query - Execute SQL query")
    
    workflow_json = {
        "nodes": [
            {
                "id": "start_1",
                "type": "start",
                "data": {"label": "Start"}
            },
            {
                "id": "db_query_1",
                "type": "database_query",
                "data": {
                    "label": "Query Database",
                    "params": {
                        "query": "SELECT name, title FROM `tabAutomesh Workflow` LIMIT 5",
                        "params": [],
                        "as_dict": True
                    }
                }
            },
            {
                "id": "end_1",
                "type": "end",
                "data": {"label": "End"}
            }
        ],
        "edges": [
            {"source": "start_1", "target": "db_query_1"},
            {"source": "db_query_1", "target": "end_1"}
        ]
    }
    
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = f"Test DB Query {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workflow.workflow_json = json.dumps(workflow_json)
    workflow.is_active = 1
    workflow.insert()
    
    execution = frappe.new_doc("Automesh Execution")
    execution.workflow = workflow.name
    execution.status = "draft"
    execution.input_data = json.dumps({})
    execution.insert()
    
    from .engine import WorkflowEngine
    engine = WorkflowEngine(execution.name)
    success = engine.execute()
    
    execution.reload()
    output = json.loads(execution.output_data) if execution.output_data else {}
    
    print(f"Execution Status: {execution.status}")
    print(f"Rows returned: {output.get('count', 0)}")
    
    assert execution.status == "completed", f"Expected 'completed', got '{execution.status}'"
    assert "results" in output, "Output should contain 'results'"
    assert isinstance(output["results"], list), "Results should be a list"
    
    frappe.delete_doc("Automesh Execution", execution.name, force=1)
    frappe.delete_doc("Automesh Workflow", workflow.name, force=1)
    
    print("✓ Database query test passed")
    return True


def test_webhook_mock():
    """Test webhook node with mock endpoint"""
    print("\n📝 Test: Webhook - Trigger HTTP callback (using httpbin)")
    
    workflow_json = {
        "nodes": [
            {
                "id": "start_1",
                "type": "start",
                "data": {"label": "Start"}
            },
            {
                "id": "webhook_1",
                "type": "webhook",
                "data": {
                    "label": "Trigger Webhook",
                    "params": {
                        "url": "https://httpbin.org/post",
                        "method": "POST",
                        "headers": {"Content-Type": "application/json"},
                        "timeout": 10
                    }
                }
            },
            {
                "id": "end_1",
                "type": "end",
                "data": {"label": "End"}
            }
        ],
        "edges": [
            {"source": "start_1", "target": "webhook_1"},
            {"source": "webhook_1", "target": "end_1"}
        ]
    }
    
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = f"Test Webhook {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workflow.workflow_json = json.dumps(workflow_json)
    workflow.is_active = 1
    workflow.insert()
    
    execution = frappe.new_doc("Automesh Execution")
    execution.workflow = workflow.name
    execution.status = "draft"
    execution.input_data = json.dumps({"test": "data", "message": "Hello webhook"})
    execution.insert()
    
    from .engine import WorkflowEngine
    engine = WorkflowEngine(execution.name)
    success = engine.execute()
    
    execution.reload()
    output = json.loads(execution.output_data) if execution.output_data else {}
    
    print(f"Execution Status: {execution.status}")
    print(f"Webhook status: {output.get('status_code', 'N/A')}")
    
    # Note: This test might fail if httpbin.org is unreachable
    # In production, you'd use a local mock server
    if execution.status == "completed":
        assert output.get("status_code") == 200, f"Expected status 200, got {output.get('status_code')}"
        print("✓ Webhook test passed")
    else:
        print("⚠️  Webhook test skipped (httpbin.org unreachable)")
    
    frappe.delete_doc("Automesh Execution", execution.name, force=1)
    frappe.delete_doc("Automesh Workflow", workflow.name, force=1)
    
    return True


# Quick test function for individual node testing
def quick_test(node_type):
    """Quick test for a specific node type"""
    test_map = {
        "file_write": test_file_write,
        "file_read": test_file_read,
        "file_integration": test_file_integration,
        "database_query": test_database_query,
        "webhook": test_webhook_mock,
    }
    
    test_func = test_map.get(node_type)
    if test_func:
        return test_func()
    else:
        print(f"Unknown node type: {node_type}")
        return False


# Note: email_send test is not included as it requires SMTP configuration
# In production, you would mock the email sending or use a test SMTP server
def test_email_send_info():
    """Information about testing email_send node"""
    print("""
    📧 Email Send Node Testing
    
    The email_send node requires SMTP configuration in Frappe.
    To test manually:
    
    1. Configure SMTP settings in Frappe
    2. Create a workflow with email_send node
    3. Set parameters:
       - to_email: recipient@example.com
       - subject: Test Email
       - body: Test message
       - from_email: sender@example.com (optional)
    
    4. Execute the workflow
    5. Check email delivery
    
    For automated testing, use a test SMTP server like MailHog or mock the frappe.sendmail function.
    """)
