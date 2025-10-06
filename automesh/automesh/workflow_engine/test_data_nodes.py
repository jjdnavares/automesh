"""
Test suite for data & integration workflow nodes

This module contains comprehensive tests for the medium-priority data & integration nodes.

Usage:
    bench --site [site-name] execute automesh.automesh.workflow_engine.test_data_nodes.run_all_tests
"""

import frappe
import json
from datetime import datetime


def run_all_tests():
    """Run all data & integration node tests"""
    print("\n" + "="*80)
    print("DATA & INTEGRATION NODES - TEST SUITE")
    print("="*80)
    
    tests = [
        ("JSON Parse Node", test_json_parse),
        ("JSON Stringify Node", test_json_stringify),
        ("XML Parse Node", test_xml_parse),
        ("XML Build Node", test_xml_build),
        ("CSV Parse Node", test_csv_parse),
        ("CSV Build Node", test_csv_build),
        ("Template Node (Jinja2)", test_template),
        ("Regex Node - Match", test_regex_match),
        ("Regex Node - Replace", test_regex_replace),
        ("Code Node", test_code),
        ("Function Node (Sub-workflow)", test_function),
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


def test_json_parse():
    """Test JSON parse node"""
    print("\n📝 Test: JSON Parse - Parse JSON string to object")
    
    workflow_json = {
        "nodes": [
            {
                "id": "start_1",
                "type": "start",
                "data": {"label": "Start"}
            },
            {
                "id": "json_parse_1",
                "type": "json_parse",
                "data": {
                    "label": "Parse JSON",
                    "params": {
                        "json_string_path": "json_string",
                        "strict": True
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
            {"source": "start_1", "target": "json_parse_1"},
            {"source": "json_parse_1", "target": "end_1"}
        ]
    }
    
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = f"Test JSON Parse {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workflow.workflow_json = json.dumps(workflow_json)
    workflow.is_active = 1
    workflow.insert()
    
    execution = frappe.new_doc("Automesh Execution")
    execution.workflow = workflow.name
    execution.status = "draft"
    execution.input_data = json.dumps({
        "json_string": '{"name": "John", "age": 30, "city": "New York"}'
    })
    execution.insert()
    
    from .engine import WorkflowEngine
    engine = WorkflowEngine(execution.name)
    success = engine.execute()
    
    execution.reload()
    output = json.loads(execution.output_data) if execution.output_data else {}
    
    print(f"Execution Status: {execution.status}")
    print(f"Output: {json.dumps(output, indent=2)}")
    
    assert execution.status == "completed", f"Expected 'completed', got '{execution.status}'"
    assert "parsed_data" in output, "Output should contain 'parsed_data'"
    assert output["parsed_data"]["name"] == "John", "Parsed data should contain correct values"
    
    frappe.delete_doc("Automesh Execution", execution.name, force=1)
    frappe.delete_doc("Automesh Workflow", workflow.name, force=1)
    
    print("✓ JSON parse test passed")
    return True


def test_json_stringify():
    """Test JSON stringify node"""
    print("\n📝 Test: JSON Stringify - Convert object to JSON string")
    
    workflow_json = {
        "nodes": [
            {
                "id": "start_1",
                "type": "start",
                "data": {"label": "Start"}
            },
            {
                "id": "json_stringify_1",
                "type": "json_stringify",
                "data": {
                    "label": "Stringify JSON",
                    "params": {
                        "indent": 2,
                        "sort_keys": True
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
            {"source": "start_1", "target": "json_stringify_1"},
            {"source": "json_stringify_1", "target": "end_1"}
        ]
    }
    
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = f"Test JSON Stringify {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workflow.workflow_json = json.dumps(workflow_json)
    workflow.is_active = 1
    workflow.insert()
    
    execution = frappe.new_doc("Automesh Execution")
    execution.workflow = workflow.name
    execution.status = "draft"
    execution.input_data = json.dumps({
        "name": "Alice",
        "age": 25,
        "skills": ["Python", "JavaScript"]
    })
    execution.insert()
    
    from .engine import WorkflowEngine
    engine = WorkflowEngine(execution.name)
    success = engine.execute()
    
    execution.reload()
    output = json.loads(execution.output_data) if execution.output_data else {}
    
    print(f"Execution Status: {execution.status}")
    print(f"Output length: {output.get('length', 0)} characters")
    
    assert execution.status == "completed", f"Expected 'completed', got '{execution.status}'"
    assert "json_string" in output, "Output should contain 'json_string'"
    assert output["length"] > 0, "JSON string should have content"
    
    frappe.delete_doc("Automesh Execution", execution.name, force=1)
    frappe.delete_doc("Automesh Workflow", workflow.name, force=1)
    
    print("✓ JSON stringify test passed")
    return True


def test_xml_parse():
    """Test XML parse node"""
    print("\n📝 Test: XML Parse - Parse XML string to dict")
    
    workflow_json = {
        "nodes": [
            {
                "id": "start_1",
                "type": "start",
                "data": {"label": "Start"}
            },
            {
                "id": "xml_parse_1",
                "type": "xml_parse",
                "data": {
                    "label": "Parse XML",
                    "params": {
                        "xml_string_path": "xml_string"
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
            {"source": "start_1", "target": "xml_parse_1"},
            {"source": "xml_parse_1", "target": "end_1"}
        ]
    }
    
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = f"Test XML Parse {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workflow.workflow_json = json.dumps(workflow_json)
    workflow.is_active = 1
    workflow.insert()
    
    execution = frappe.new_doc("Automesh Execution")
    execution.workflow = workflow.name
    execution.status = "draft"
    execution.input_data = json.dumps({
        "xml_string": '<person><name>Bob</name><age>35</age></person>'
    })
    execution.insert()
    
    from .engine import WorkflowEngine
    engine = WorkflowEngine(execution.name)
    success = engine.execute()
    
    execution.reload()
    output = json.loads(execution.output_data) if execution.output_data else {}
    
    print(f"Execution Status: {execution.status}")
    print(f"Root tag: {output.get('root_tag', 'N/A')}")
    
    assert execution.status == "completed", f"Expected 'completed', got '{execution.status}'"
    assert "parsed_data" in output, "Output should contain 'parsed_data'"
    assert output["root_tag"] == "person", "Root tag should be 'person'"
    
    frappe.delete_doc("Automesh Execution", execution.name, force=1)
    frappe.delete_doc("Automesh Workflow", workflow.name, force=1)
    
    print("✓ XML parse test passed")
    return True


def test_xml_build():
    """Test XML build node"""
    print("\n📝 Test: XML Build - Build XML from dict")
    
    workflow_json = {
        "nodes": [
            {
                "id": "start_1",
                "type": "start",
                "data": {"label": "Start"}
            },
            {
                "id": "xml_build_1",
                "type": "xml_build",
                "data": {
                    "label": "Build XML",
                    "params": {
                        "root_tag": "user",
                        "pretty_print": True
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
            {"source": "start_1", "target": "xml_build_1"},
            {"source": "xml_build_1", "target": "end_1"}
        ]
    }
    
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = f"Test XML Build {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workflow.workflow_json = json.dumps(workflow_json)
    workflow.is_active = 1
    workflow.insert()
    
    execution = frappe.new_doc("Automesh Execution")
    execution.workflow = workflow.name
    execution.status = "draft"
    execution.input_data = json.dumps({
        "name": "Charlie",
        "email": "charlie@example.com"
    })
    execution.insert()
    
    from .engine import WorkflowEngine
    engine = WorkflowEngine(execution.name)
    success = engine.execute()
    
    execution.reload()
    output = json.loads(execution.output_data) if execution.output_data else {}
    
    print(f"Execution Status: {execution.status}")
    print(f"XML length: {output.get('length', 0)} characters")
    
    assert execution.status == "completed", f"Expected 'completed', got '{execution.status}'"
    assert "xml_string" in output, "Output should contain 'xml_string'"
    assert output["root_tag"] == "user", "Root tag should be 'user'"
    
    frappe.delete_doc("Automesh Execution", execution.name, force=1)
    frappe.delete_doc("Automesh Workflow", workflow.name, force=1)
    
    print("✓ XML build test passed")
    return True


def test_csv_parse():
    """Test CSV parse node"""
    print("\n📝 Test: CSV Parse - Parse CSV string to array")
    
    workflow_json = {
        "nodes": [
            {
                "id": "start_1",
                "type": "start",
                "data": {"label": "Start"}
            },
            {
                "id": "csv_parse_1",
                "type": "csv_parse",
                "data": {
                    "label": "Parse CSV",
                    "params": {
                        "csv_string_path": "csv_string",
                        "delimiter": ",",
                        "has_header": True
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
            {"source": "start_1", "target": "csv_parse_1"},
            {"source": "csv_parse_1", "target": "end_1"}
        ]
    }
    
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = f"Test CSV Parse {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workflow.workflow_json = json.dumps(workflow_json)
    workflow.is_active = 1
    workflow.insert()
    
    execution = frappe.new_doc("Automesh Execution")
    execution.workflow = workflow.name
    execution.status = "draft"
    execution.input_data = json.dumps({
        "csv_string": "name,age,city\nAlice,30,NYC\nBob,25,LA\nCharlie,35,SF"
    })
    execution.insert()
    
    from .engine import WorkflowEngine
    engine = WorkflowEngine(execution.name)
    success = engine.execute()
    
    execution.reload()
    output = json.loads(execution.output_data) if execution.output_data else {}
    
    print(f"Execution Status: {execution.status}")
    print(f"Row count: {output.get('row_count', 0)}")
    
    assert execution.status == "completed", f"Expected 'completed', got '{execution.status}'"
    assert "parsed_data" in output, "Output should contain 'parsed_data'"
    assert output["row_count"] == 3, f"Expected 3 rows, got {output.get('row_count')}"
    
    frappe.delete_doc("Automesh Execution", execution.name, force=1)
    frappe.delete_doc("Automesh Workflow", workflow.name, force=1)
    
    print("✓ CSV parse test passed")
    return True


def test_csv_build():
    """Test CSV build node"""
    print("\n📝 Test: CSV Build - Build CSV from array")
    
    workflow_json = {
        "nodes": [
            {
                "id": "start_1",
                "type": "start",
                "data": {"label": "Start"}
            },
            {
                "id": "csv_build_1",
                "type": "csv_build",
                "data": {
                    "label": "Build CSV",
                    "params": {
                        "data_path": "users",
                        "delimiter": ",",
                        "include_header": True
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
            {"source": "start_1", "target": "csv_build_1"},
            {"source": "csv_build_1", "target": "end_1"}
        ]
    }
    
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = f"Test CSV Build {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workflow.workflow_json = json.dumps(workflow_json)
    workflow.is_active = 1
    workflow.insert()
    
    execution = frappe.new_doc("Automesh Execution")
    execution.workflow = workflow.name
    execution.status = "draft"
    execution.input_data = json.dumps({
        "users": [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]
    })
    execution.insert()
    
    from .engine import WorkflowEngine
    engine = WorkflowEngine(execution.name)
    success = engine.execute()
    
    execution.reload()
    output = json.loads(execution.output_data) if execution.output_data else {}
    
    print(f"Execution Status: {execution.status}")
    print(f"CSV length: {output.get('length', 0)} characters")
    
    assert execution.status == "completed", f"Expected 'completed', got '{execution.status}'"
    assert "csv_string" in output, "Output should contain 'csv_string'"
    assert output["row_count"] == 2, f"Expected 2 rows, got {output.get('row_count')}"
    
    frappe.delete_doc("Automesh Execution", execution.name, force=1)
    frappe.delete_doc("Automesh Workflow", workflow.name, force=1)
    
    print("✓ CSV build test passed")
    return True


def test_template():
    """Test template node with Jinja2"""
    print("\n📝 Test: Template - Render Jinja2 template")
    
    workflow_json = {
        "nodes": [
            {
                "id": "start_1",
                "type": "start",
                "data": {"label": "Start"}
            },
            {
                "id": "template_1",
                "type": "template",
                "data": {
                    "label": "Render Template",
                    "params": {
                        "template_string": "Hello {{ name }}! You are {{ age }} years old."
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
            {"source": "start_1", "target": "template_1"},
            {"source": "template_1", "target": "end_1"}
        ]
    }
    
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = f"Test Template {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workflow.workflow_json = json.dumps(workflow_json)
    workflow.is_active = 1
    workflow.insert()
    
    execution = frappe.new_doc("Automesh Execution")
    execution.workflow = workflow.name
    execution.status = "draft"
    execution.input_data = json.dumps({
        "name": "David",
        "age": 28
    })
    execution.insert()
    
    from .engine import WorkflowEngine
    engine = WorkflowEngine(execution.name)
    success = engine.execute()
    
    execution.reload()
    output = json.loads(execution.output_data) if execution.output_data else {}
    
    print(f"Execution Status: {execution.status}")
    print(f"Rendered: {output.get('rendered', 'N/A')}")
    
    assert execution.status == "completed", f"Expected 'completed', got '{execution.status}'"
    assert "rendered" in output, "Output should contain 'rendered'"
    assert "David" in output["rendered"], "Rendered text should contain name"
    
    frappe.delete_doc("Automesh Execution", execution.name, force=1)
    frappe.delete_doc("Automesh Workflow", workflow.name, force=1)
    
    print("✓ Template test passed")
    return True


def test_regex_match():
    """Test regex node with match operation"""
    print("\n📝 Test: Regex - Match pattern")
    
    workflow_json = {
        "nodes": [
            {
                "id": "start_1",
                "type": "start",
                "data": {"label": "Start"}
            },
            {
                "id": "regex_1",
                "type": "regex",
                "data": {
                    "label": "Regex Match",
                    "params": {
                        "pattern": r"(\w+)@(\w+\.\w+)",
                        "operation": "search",
                        "text_path": "text"
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
            {"source": "start_1", "target": "regex_1"},
            {"source": "regex_1", "target": "end_1"}
        ]
    }
    
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = f"Test Regex {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workflow.workflow_json = json.dumps(workflow_json)
    workflow.is_active = 1
    workflow.insert()
    
    execution = frappe.new_doc("Automesh Execution")
    execution.workflow = workflow.name
    execution.status = "draft"
    execution.input_data = json.dumps({
        "text": "Contact us at support@example.com for help"
    })
    execution.insert()
    
    from .engine import WorkflowEngine
    engine = WorkflowEngine(execution.name)
    success = engine.execute()
    
    execution.reload()
    output = json.loads(execution.output_data) if execution.output_data else {}
    
    print(f"Execution Status: {execution.status}")
    print(f"Found: {output.get('result', {}).get('found', False)}")
    
    assert execution.status == "completed", f"Expected 'completed', got '{execution.status}'"
    assert output.get("result", {}).get("found") == True, "Should find email pattern"
    
    frappe.delete_doc("Automesh Execution", execution.name, force=1)
    frappe.delete_doc("Automesh Workflow", workflow.name, force=1)
    
    print("✓ Regex match test passed")
    return True


def test_regex_replace():
    """Test regex node with replace operation"""
    print("\n📝 Test: Regex - Replace pattern")
    
    workflow_json = {
        "nodes": [
            {
                "id": "start_1",
                "type": "start",
                "data": {"label": "Start"}
            },
            {
                "id": "regex_1",
                "type": "regex",
                "data": {
                    "label": "Regex Replace",
                    "params": {
                        "pattern": r"\d+",
                        "operation": "replace",
                        "replacement": "XXX",
                        "text_path": "text"
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
            {"source": "start_1", "target": "regex_1"},
            {"source": "regex_1", "target": "end_1"}
        ]
    }
    
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = f"Test Regex Replace {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workflow.workflow_json = json.dumps(workflow_json)
    workflow.is_active = 1
    workflow.insert()
    
    execution = frappe.new_doc("Automesh Execution")
    execution.workflow = workflow.name
    execution.status = "draft"
    execution.input_data = json.dumps({
        "text": "My phone is 123-456-7890"
    })
    execution.insert()
    
    from .engine import WorkflowEngine
    engine = WorkflowEngine(execution.name)
    success = engine.execute()
    
    execution.reload()
    output = json.loads(execution.output_data) if execution.output_data else {}
    
    print(f"Execution Status: {execution.status}")
    print(f"Replaced: {output.get('result', {}).get('replaced', 'N/A')}")
    
    assert execution.status == "completed", f"Expected 'completed', got '{execution.status}'"
    assert output.get("result", {}).get("changed") == True, "Text should be changed"
    
    frappe.delete_doc("Automesh Execution", execution.name, force=1)
    frappe.delete_doc("Automesh Workflow", workflow.name, force=1)
    
    print("✓ Regex replace test passed")
    return True


def test_code():
    """Test code node with custom Python"""
    print("\n📝 Test: Code - Execute custom Python code")
    
    workflow_json = {
        "nodes": [
            {
                "id": "start_1",
                "type": "start",
                "data": {"label": "Start"}
            },
            {
                "id": "code_1",
                "type": "code",
                "data": {
                    "label": "Execute Code",
                    "params": {
                        "code_string": "output = sum(input['numbers'])"
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
            {"source": "start_1", "target": "code_1"},
            {"source": "code_1", "target": "end_1"}
        ]
    }
    
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = f"Test Code {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workflow.workflow_json = json.dumps(workflow_json)
    workflow.is_active = 1
    workflow.insert()
    
    execution = frappe.new_doc("Automesh Execution")
    execution.workflow = workflow.name
    execution.status = "draft"
    execution.input_data = json.dumps({
        "numbers": [1, 2, 3, 4, 5]
    })
    execution.insert()
    
    from .engine import WorkflowEngine
    engine = WorkflowEngine(execution.name)
    success = engine.execute()
    
    execution.reload()
    output = json.loads(execution.output_data) if execution.output_data else {}
    
    print(f"Execution Status: {execution.status}")
    print(f"Result: {output.get('result', 'N/A')}")
    
    assert execution.status == "completed", f"Expected 'completed', got '{execution.status}'"
    assert output.get("result") == 15, f"Expected 15, got {output.get('result')}"
    
    frappe.delete_doc("Automesh Execution", execution.name, force=1)
    frappe.delete_doc("Automesh Workflow", workflow.name, force=1)
    
    print("✓ Code test passed")
    return True


def test_function():
    """Test function node with sub-workflow call"""
    print("\n📝 Test: Function - Call sub-workflow")
    
    # Create a simple sub-workflow first
    sub_workflow_json = {
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "end", "type": "end"}
        ],
        "edges": [
            {"source": "start", "target": "end"}
        ]
    }
    
    sub_workflow = frappe.new_doc("Automesh Workflow")
    sub_workflow.title = f"Sub Workflow {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    sub_workflow.workflow_json = json.dumps(sub_workflow_json)
    sub_workflow.is_active = 1
    sub_workflow.insert()
    
    # Create main workflow that calls sub-workflow
    workflow_json = {
        "nodes": [
            {
                "id": "start_1",
                "type": "start",
                "data": {"label": "Start"}
            },
            {
                "id": "function_1",
                "type": "function",
                "data": {
                    "label": "Call Sub-workflow",
                    "params": {
                        "workflow_name": sub_workflow.name
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
            {"source": "start_1", "target": "function_1"},
            {"source": "function_1", "target": "end_1"}
        ]
    }
    
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.title = f"Test Function {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workflow.workflow_json = json.dumps(workflow_json)
    workflow.is_active = 1
    workflow.insert()
    
    execution = frappe.new_doc("Automesh Execution")
    execution.workflow = workflow.name
    execution.status = "draft"
    execution.input_data = json.dumps({"test": "data"})
    execution.insert()
    
    from .engine import WorkflowEngine
    engine = WorkflowEngine(execution.name)
    success = engine.execute()
    
    execution.reload()
    output = json.loads(execution.output_data) if execution.output_data else {}
    
    print(f"Execution Status: {execution.status}")
    print(f"Sub-workflow status: {output.get('status', 'N/A')}")
    
    assert execution.status == "completed", f"Expected 'completed', got '{execution.status}'"
    assert "workflow_name" in output, "Output should contain workflow_name"
    
    frappe.delete_doc("Automesh Execution", execution.name, force=1)
    frappe.delete_doc("Automesh Workflow", workflow.name, force=1)
    frappe.delete_doc("Automesh Workflow", sub_workflow.name, force=1)
    
    print("✓ Function test passed")
    return True


# Quick test function for individual node testing
def quick_test(node_type):
    """Quick test for a specific node type"""
    test_map = {
        "json_parse": test_json_parse,
        "json_stringify": test_json_stringify,
        "xml_parse": test_xml_parse,
        "xml_build": test_xml_build,
        "csv_parse": test_csv_parse,
        "csv_build": test_csv_build,
        "template": test_template,
        "regex": test_regex_match,
        "code": test_code,
        "function": test_function,
    }
    
    test_func = test_map.get(node_type)
    if test_func:
        return test_func()
    else:
        print(f"Unknown node type: {node_type}")
        return False
