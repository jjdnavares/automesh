"""
Verification script for essential workflow nodes

This script verifies that all 6 essential workflow nodes are properly registered
and ready for use.

Usage:
    bench --site [site-name] execute automesh.automesh.workflow_engine.verify_essential_nodes.verify
"""

import frappe
from .node_handlers import NodeHandlerRegistry


def verify():
    """Verify all essential nodes are properly registered"""
    print("\n" + "="*80)
    print("ESSENTIAL WORKFLOW NODES - VERIFICATION")
    print("="*80 + "\n")
    
    # Expected nodes
    essential_nodes = [
        ("loop", "LoopNodeHandler"),
        ("for_each", "LoopNodeHandler"),
        ("parallel", "ParallelNodeHandler"),
        ("merge", "MergeNodeHandler"),
        ("switch", "SwitchNodeHandler"),
        ("set_variable", "SetVariableNodeHandler"),
        ("get_variable", "GetVariableNodeHandler"),
    ]
    
    print("Checking node registrations...\n")
    
    all_passed = True
    
    for node_type, expected_class in essential_nodes:
        handler = NodeHandlerRegistry.get_handler(node_type)
        
        if handler:
            handler_name = handler.__name__
            status = "✅" if handler_name == expected_class else "⚠️"
            
            if handler_name == expected_class:
                print(f"{status} {node_type:20s} -> {handler_name}")
            else:
                print(f"{status} {node_type:20s} -> {handler_name} (expected {expected_class})")
                all_passed = False
        else:
            print(f"❌ {node_type:20s} -> NOT REGISTERED")
            all_passed = False
    
    print("\n" + "-"*80)
    
    # Get all registered nodes
    all_registered = NodeHandlerRegistry.get_all_registered_types()
    
    print(f"\nTotal registered node types: {len(all_registered)}")
    print(f"Essential nodes verified: {len(essential_nodes)}")
    
    # Count by category
    production_nodes = [
        "start", "end", "condition", "delay", "http_request", "transform",
        "frappe_doc_create", "frappe_doc_update", "frappe_doc_get", 
        "frappe_doc_delete", "frappe_doc_list",
        "loop", "for_each", "parallel", "merge", "switch", 
        "set_variable", "get_variable"
    ]
    
    test_nodes = [
        "test_echo", "test_random", "test_delay", "test_math", 
        "test_error", "test_transform"
    ]
    
    writer_nodes = [
        "writer_generate_content", "writer_custom_prompt", "writer_get_content"
    ]
    
    production_count = sum(1 for n in production_nodes if n in all_registered)
    test_count = sum(1 for n in test_nodes if n in all_registered)
    writer_count = sum(1 for n in writer_nodes if n in all_registered)
    
    print(f"\nNode breakdown:")
    print(f"  Production nodes: {production_count}")
    print(f"  Test nodes: {test_count}")
    print(f"  Writer nodes: {writer_count}")
    print(f"  Total: {production_count + test_count + writer_count}")
    
    print("\n" + "="*80)
    
    if all_passed:
        print("✅ VERIFICATION PASSED - All essential nodes registered correctly!")
    else:
        print("❌ VERIFICATION FAILED - Some nodes missing or incorrect!")
    
    print("="*80 + "\n")
    
    return all_passed


def list_all_nodes():
    """List all registered node types"""
    print("\n" + "="*80)
    print("ALL REGISTERED NODE TYPES")
    print("="*80 + "\n")
    
    all_nodes = sorted(NodeHandlerRegistry.get_all_registered_types())
    
    # Categorize nodes
    categories = {
        "Core Workflow": ["start", "end", "condition", "delay"],
        "HTTP & API": ["http_request"],
        "Data Transformation": ["transform"],
        "Frappe Integration": [
            "frappe_doc_create", "frappe_doc_update", "frappe_doc_get",
            "frappe_doc_delete", "frappe_doc_list"
        ],
        "Essential Workflow": [
            "loop", "for_each", "parallel", "merge", "switch",
            "set_variable", "get_variable"
        ],
        "Writer AI": [
            "writer_generate_content", "writer_custom_prompt", "writer_get_content"
        ],
        "Test Nodes": [
            "test_echo", "test_random", "test_delay", "test_math",
            "test_error", "test_transform"
        ]
    }
    
    for category, nodes in categories.items():
        registered = [n for n in nodes if n in all_nodes]
        if registered:
            print(f"\n{category} ({len(registered)} nodes):")
            for node in registered:
                handler = NodeHandlerRegistry.get_handler(node)
                print(f"  ✅ {node:30s} -> {handler.__name__}")
    
    # Show any uncategorized nodes
    categorized = [n for nodes in categories.values() for n in nodes]
    uncategorized = [n for n in all_nodes if n not in categorized]
    
    if uncategorized:
        print(f"\nOther Nodes ({len(uncategorized)}):")
        for node in uncategorized:
            handler = NodeHandlerRegistry.get_handler(node)
            print(f"  ✅ {node:30s} -> {handler.__name__}")
    
    print(f"\n{'='*80}")
    print(f"Total: {len(all_nodes)} registered node types")
    print(f"{'='*80}\n")


def quick_info():
    """Show quick information about essential nodes"""
    print("\n" + "="*80)
    print("ESSENTIAL NODES - QUICK INFO")
    print("="*80 + "\n")
    
    nodes_info = [
        {
            "name": "loop / for_each",
            "purpose": "Iterate over arrays/collections",
            "key_params": "items_path, item_variable_name, index_variable_name"
        },
        {
            "name": "parallel",
            "purpose": "Execute multiple branches in parallel",
            "key_params": "None (uses outgoing connections)"
        },
        {
            "name": "merge",
            "purpose": "Merge multiple data streams",
            "key_params": "merge_strategy (first, last, all, object, array)"
        },
        {
            "name": "switch",
            "purpose": "Multi-way branching",
            "key_params": "switch_value_path, cases, default_case"
        },
        {
            "name": "set_variable",
            "purpose": "Set workflow variables",
            "key_params": "variable_name, variable_value, value_from_input"
        },
        {
            "name": "get_variable",
            "purpose": "Retrieve workflow variables",
            "key_params": "variable_name, default_value"
        }
    ]
    
    for i, node in enumerate(nodes_info, 1):
        print(f"{i}. {node['name']}")
        print(f"   Purpose: {node['purpose']}")
        print(f"   Key Params: {node['key_params']}")
        print()
    
    print("="*80)
    print("For full documentation, see: ESSENTIAL_NODES_IMPLEMENTATION.md")
    print("For quick reference, see: ESSENTIAL_NODES_QUICK_REFERENCE.md")
    print("="*80 + "\n")
