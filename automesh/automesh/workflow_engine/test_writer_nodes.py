"""
Test script for Writer integration nodes

This script tests the Writer nodes to ensure they work correctly.

Usage:
    bench console
    >>> from automesh.workflow_engine.test_writer_nodes import test_writer_nodes
    >>> test_writer_nodes()
"""

import frappe
from .writer_nodes import (
    WriterGenerateContentNodeHandler,
    WriterCustomPromptNodeHandler,
    WriterGetContentNodeHandler
)


class MockExecutionContext:
    """Mock execution context for testing"""
    
    def __init__(self):
        self.variables = {}
        self.node_outputs = {}
        self.logs = []
        self.connections = {}
    
    def get_variable(self, name, default=None):
        return self.variables.get(name, default)
    
    def set_node_output(self, node_id, output):
        self.node_outputs[node_id] = output
    
    def get_node_output(self, node_id):
        return self.node_outputs.get(node_id)
    
    def log(self, node_id, level, message):
        self.logs.append({"node_id": node_id, "level": level, "message": message})
        print(f"[{level}] {message}")
    
    def get_incoming_connections(self, node_id):
        return self.connections.get(node_id, [])
    
    def get_all_variables(self):
        return self.variables


def test_writer_generate_content():
    """Test the Writer Generate Content node"""
    
    print("\n" + "="*60)
    print("Testing Writer Generate Content Node")
    print("="*60 + "\n")
    
    # Check if Writer app is installed
    if not frappe.db.exists("DocType", "Generated Content"):
        print("⚠ Writer app is not installed. Skipping test.")
        return False
    
    # Create mock node data
    node_data = {
        "id": "test_node_1",
        "type": "writer_generate_content",
        "data": {
            "params": {
                "keyword": "Artificial Intelligence in Healthcare",
                "content_type": "Blog Post",
                "tone": "Professional",
                "provider": "openai",
                "model": "gpt-4"
            }
        }
    }
    
    # Create execution context
    context = MockExecutionContext()
    
    # Create node handler
    handler = WriterGenerateContentNodeHandler(node_data, context)
    
    try:
        # Execute the node
        print("Executing node...")
        result = handler.execute()
        
        if result["success"]:
            print("\n✓ Node executed successfully!")
            print(f"  Title: {result['data'].get('title')}")
            print(f"  Doc Name: {result['data'].get('doc_name')}")
            print(f"  Generated Text Length: {len(result['data'].get('generated_text', ''))} characters")
            return True
        else:
            print(f"\n✗ Node execution failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\n✗ Exception during execution: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Writer Node Test Error")
        return False


def test_writer_custom_prompt():
    """Test the Writer Custom Prompt node"""
    
    print("\n" + "="*60)
    print("Testing Writer Custom Prompt Node")
    print("="*60 + "\n")
    
    # Create mock node data
    node_data = {
        "id": "test_node_2",
        "type": "writer_custom_prompt",
        "data": {
            "params": {
                "prompt": "Write a short tagline for a company that sells eco-friendly products.",
                "provider": "openai",
                "model": "gpt-4"
            }
        }
    }
    
    # Create execution context
    context = MockExecutionContext()
    
    # Create node handler
    handler = WriterCustomPromptNodeHandler(node_data, context)
    
    try:
        # Execute the node
        print("Executing node...")
        result = handler.execute()
        
        if result["success"]:
            print("\n✓ Node executed successfully!")
            print(f"  Generated Text: {result['data'].get('generated_text')}")
            return True
        else:
            print(f"\n✗ Node execution failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\n✗ Exception during execution: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Writer Custom Prompt Test Error")
        return False


def test_writer_get_content():
    """Test the Writer Get Content node"""
    
    print("\n" + "="*60)
    print("Testing Writer Get Content Node")
    print("="*60 + "\n")
    
    # Check if Writer app is installed
    if not frappe.db.exists("DocType", "Generated Content"):
        print("⚠ Writer app is not installed. Skipping test.")
        return False
    
    # Create mock node data
    node_data = {
        "id": "test_node_3",
        "type": "writer_get_content",
        "data": {
            "params": {
                "limit": 5,
                "keyword_filter": "",
                "content_type_filter": ""
            }
        }
    }
    
    # Create execution context
    context = MockExecutionContext()
    
    # Create node handler
    handler = WriterGetContentNodeHandler(node_data, context)
    
    try:
        # Execute the node
        print("Executing node...")
        result = handler.execute()
        
        if result["success"]:
            print("\n✓ Node executed successfully!")
            print(f"  Retrieved {result['data'].get('count')} content(s)")
            
            if result['data'].get('count') > 0:
                print("\n  Sample content:")
                for i, content in enumerate(result['data'].get('contents', [])[:3], 1):
                    print(f"    {i}. {content.get('title')} ({content.get('content_type')})")
            
            return True
        else:
            print(f"\n✗ Node execution failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\n✗ Exception during execution: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Writer Get Content Test Error")
        return False


def test_writer_nodes():
    """Run all Writer node tests"""
    
    print("\n" + "#"*60)
    print("# Writer Nodes Test Suite")
    print("#"*60)
    
    results = {
        "generate_content": test_writer_generate_content(),
        "custom_prompt": test_writer_custom_prompt(),
        "get_content": test_writer_get_content()
    }
    
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60 + "\n")
    
    return results


if __name__ == "__main__":
    test_writer_nodes()
