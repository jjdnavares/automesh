"""
Script to add dummy workflow data for testing Phase 1: Core CRUD Operations
"""

import frappe
from frappe.utils import now, add_days
import json


def create_dummy_workflows():
    """Create dummy workflows for testing"""
    
    # Clear existing workflows (optional - comment out if you want to keep existing data)
    # frappe.db.delete("Automesh Workflow")
    # frappe.db.commit()
    
    workflows = [
        {
            "title": "Customer Onboarding Automation",
            "description": "Automatically onboard new customers with welcome emails and account setup",
            "version": "1.0.0",
            "is_active": 1,
            "tags": "automation, customer, onboarding",
            "workflow_json": json.dumps({
                "nodes": [
                    {
                        "id": "start-1",
                        "type": "start",
                        "position": {"x": 100, "y": 100},
                        "data": {"label": "Start", "type": "start"}
                    },
                    {
                        "id": "http-1",
                        "type": "http_request",
                        "position": {"x": 300, "y": 100},
                        "data": {"label": "Fetch Customer Data", "type": "http_request"}
                    },
                    {
                        "id": "frappe-1",
                        "type": "frappe_doc_create",
                        "position": {"x": 500, "y": 100},
                        "data": {"label": "Create Customer Record", "type": "frappe_doc_create"}
                    },
                    {
                        "id": "end-1",
                        "type": "end",
                        "position": {"x": 700, "y": 100},
                        "data": {"label": "End", "type": "end"}
                    }
                ],
                "edges": [
                    {"id": "e1", "source": "start-1", "target": "http-1"},
                    {"id": "e2", "source": "http-1", "target": "frappe-1"},
                    {"id": "e3", "source": "frappe-1", "target": "end-1"}
                ]
            }),
            "execution_count": 45,
            "last_executed_at": now()
        },
        {
            "title": "Daily Report Generator",
            "description": "Generate and email daily sales reports to management",
            "version": "1.2.0",
            "is_active": 1,
            "tags": "reporting, automation, sales",
            "workflow_json": json.dumps({
                "nodes": [
                    {
                        "id": "start-1",
                        "type": "start",
                        "position": {"x": 100, "y": 100},
                        "data": {"label": "Start", "type": "start"}
                    },
                    {
                        "id": "frappe-list-1",
                        "type": "frappe_doc_list",
                        "position": {"x": 300, "y": 100},
                        "data": {"label": "Get Sales Data", "type": "frappe_doc_list"}
                    },
                    {
                        "id": "transform-1",
                        "type": "transform",
                        "position": {"x": 500, "y": 100},
                        "data": {"label": "Transform Data", "type": "transform"}
                    },
                    {
                        "id": "end-1",
                        "type": "end",
                        "position": {"x": 700, "y": 100},
                        "data": {"label": "End", "type": "end"}
                    }
                ],
                "edges": [
                    {"id": "e1", "source": "start-1", "target": "frappe-list-1"},
                    {"id": "e2", "source": "frappe-list-1", "target": "transform-1"},
                    {"id": "e3", "source": "transform-1", "target": "end-1"}
                ]
            }),
            "execution_count": 127,
            "last_executed_at": add_days(now(), -1)
        },
        {
            "title": "Content Generation Pipeline",
            "description": "Generate blog posts using AI and publish to website",
            "version": "2.0.0",
            "is_active": 1,
            "tags": "content, ai, automation",
            "workflow_json": json.dumps({
                "nodes": [
                    {
                        "id": "start-1",
                        "type": "start",
                        "position": {"x": 100, "y": 100},
                        "data": {"label": "Start", "type": "start"}
                    },
                    {
                        "id": "writer-1",
                        "type": "writer_generate_content",
                        "position": {"x": 300, "y": 100},
                        "data": {"label": "Generate Content", "type": "writer_generate_content"}
                    },
                    {
                        "id": "frappe-create-1",
                        "type": "frappe_doc_create",
                        "position": {"x": 500, "y": 100},
                        "data": {"label": "Create Blog Post", "type": "frappe_doc_create"}
                    },
                    {
                        "id": "end-1",
                        "type": "end",
                        "position": {"x": 700, "y": 100},
                        "data": {"label": "End", "type": "end"}
                    }
                ],
                "edges": [
                    {"id": "e1", "source": "start-1", "target": "writer-1"},
                    {"id": "e2", "source": "writer-1", "target": "frappe-create-1"},
                    {"id": "e3", "source": "frappe-create-1", "target": "end-1"}
                ]
            }),
            "execution_count": 23,
            "last_executed_at": add_days(now(), -2)
        },
        {
            "title": "Invoice Processing Workflow",
            "description": "Process incoming invoices and update accounting records",
            "version": "1.5.0",
            "is_active": 0,
            "tags": "finance, automation, invoices",
            "workflow_json": json.dumps({
                "nodes": [
                    {
                        "id": "start-1",
                        "type": "start",
                        "position": {"x": 100, "y": 100},
                        "data": {"label": "Start", "type": "start"}
                    },
                    {
                        "id": "http-1",
                        "type": "http_request",
                        "position": {"x": 300, "y": 100},
                        "data": {"label": "Fetch Invoice", "type": "http_request"}
                    },
                    {
                        "id": "condition-1",
                        "type": "condition",
                        "position": {"x": 500, "y": 100},
                        "data": {"label": "Check Amount", "type": "condition"}
                    },
                    {
                        "id": "frappe-update-1",
                        "type": "frappe_doc_update",
                        "position": {"x": 700, "y": 50},
                        "data": {"label": "Update Record", "type": "frappe_doc_update"}
                    },
                    {
                        "id": "end-1",
                        "type": "end",
                        "position": {"x": 900, "y": 100},
                        "data": {"label": "End", "type": "end"}
                    }
                ],
                "edges": [
                    {"id": "e1", "source": "start-1", "target": "http-1"},
                    {"id": "e2", "source": "http-1", "target": "condition-1"},
                    {"id": "e3", "source": "condition-1", "target": "frappe-update-1"},
                    {"id": "e4", "source": "frappe-update-1", "target": "end-1"}
                ]
            }),
            "execution_count": 8,
            "last_executed_at": add_days(now(), -7)
        },
        {
            "title": "Data Sync Pipeline",
            "description": "Sync data between multiple systems on schedule",
            "version": "1.0.0",
            "is_active": 1,
            "tags": "integration, sync, automation",
            "workflow_json": json.dumps({
                "nodes": [
                    {
                        "id": "start-1",
                        "type": "start",
                        "position": {"x": 100, "y": 100},
                        "data": {"label": "Start", "type": "start"}
                    },
                    {
                        "id": "http-1",
                        "type": "http_request",
                        "position": {"x": 300, "y": 100},
                        "data": {"label": "Fetch from API", "type": "http_request"}
                    },
                    {
                        "id": "transform-1",
                        "type": "transform",
                        "position": {"x": 500, "y": 100},
                        "data": {"label": "Transform Data", "type": "transform"}
                    },
                    {
                        "id": "frappe-create-1",
                        "type": "frappe_doc_create",
                        "position": {"x": 700, "y": 100},
                        "data": {"label": "Save to Frappe", "type": "frappe_doc_create"}
                    },
                    {
                        "id": "end-1",
                        "type": "end",
                        "position": {"x": 900, "y": 100},
                        "data": {"label": "End", "type": "end"}
                    }
                ],
                "edges": [
                    {"id": "e1", "source": "start-1", "target": "http-1"},
                    {"id": "e2", "source": "http-1", "target": "transform-1"},
                    {"id": "e3", "source": "transform-1", "target": "frappe-create-1"},
                    {"id": "e4", "source": "frappe-create-1", "target": "end-1"}
                ]
            }),
            "execution_count": 312,
            "last_executed_at": now()
        },
        {
            "title": "Lead Qualification Bot",
            "description": "Automatically qualify and route incoming leads",
            "version": "1.1.0",
            "is_active": 1,
            "tags": "sales, automation, leads",
            "workflow_json": json.dumps({
                "nodes": [
                    {
                        "id": "start-1",
                        "type": "start",
                        "position": {"x": 100, "y": 100},
                        "data": {"label": "Start", "type": "start"}
                    },
                    {
                        "id": "frappe-get-1",
                        "type": "frappe_doc_get",
                        "position": {"x": 300, "y": 100},
                        "data": {"label": "Get Lead", "type": "frappe_doc_get"}
                    },
                    {
                        "id": "condition-1",
                        "type": "condition",
                        "position": {"x": 500, "y": 100},
                        "data": {"label": "Qualify Lead", "type": "condition"}
                    },
                    {
                        "id": "end-1",
                        "type": "end",
                        "position": {"x": 700, "y": 100},
                        "data": {"label": "End", "type": "end"}
                    }
                ],
                "edges": [
                    {"id": "e1", "source": "start-1", "target": "frappe-get-1"},
                    {"id": "e2", "source": "frappe-get-1", "target": "condition-1"},
                    {"id": "e3", "source": "condition-1", "target": "end-1"}
                ]
            }),
            "execution_count": 89,
            "last_executed_at": add_days(now(), -3)
        },
        {
            "title": "Backup Automation",
            "description": "Automated daily backup of critical data",
            "version": "1.0.0",
            "is_active": 0,
            "tags": "backup, automation, maintenance",
            "workflow_json": json.dumps({
                "nodes": [
                    {
                        "id": "start-1",
                        "type": "start",
                        "position": {"x": 100, "y": 100},
                        "data": {"label": "Start", "type": "start"}
                    },
                    {
                        "id": "frappe-list-1",
                        "type": "frappe_doc_list",
                        "position": {"x": 300, "y": 100},
                        "data": {"label": "Get Data", "type": "frappe_doc_list"}
                    },
                    {
                        "id": "http-1",
                        "type": "http_request",
                        "position": {"x": 500, "y": 100},
                        "data": {"label": "Upload to Cloud", "type": "http_request"}
                    },
                    {
                        "id": "end-1",
                        "type": "end",
                        "position": {"x": 700, "y": 100},
                        "data": {"label": "End", "type": "end"}
                    }
                ],
                "edges": [
                    {"id": "e1", "source": "start-1", "target": "frappe-list-1"},
                    {"id": "e2", "source": "frappe-list-1", "target": "http-1"},
                    {"id": "e3", "source": "http-1", "target": "end-1"}
                ]
            }),
            "execution_count": 0,
            "last_executed_at": None
        },
        {
            "title": "Email Campaign Manager",
            "description": "Manage and send email campaigns to subscribers",
            "version": "2.1.0",
            "is_active": 1,
            "tags": "email, marketing, automation",
            "workflow_json": json.dumps({
                "nodes": [
                    {
                        "id": "start-1",
                        "type": "start",
                        "position": {"x": 100, "y": 100},
                        "data": {"label": "Start", "type": "start"}
                    },
                    {
                        "id": "frappe-list-1",
                        "type": "frappe_doc_list",
                        "position": {"x": 300, "y": 100},
                        "data": {"label": "Get Subscribers", "type": "frappe_doc_list"}
                    },
                    {
                        "id": "writer-1",
                        "type": "writer_generate_content",
                        "position": {"x": 500, "y": 100},
                        "data": {"label": "Generate Email", "type": "writer_generate_content"}
                    },
                    {
                        "id": "http-1",
                        "type": "http_request",
                        "position": {"x": 700, "y": 100},
                        "data": {"label": "Send Email", "type": "http_request"}
                    },
                    {
                        "id": "end-1",
                        "type": "end",
                        "position": {"x": 900, "y": 100},
                        "data": {"label": "End", "type": "end"}
                    }
                ],
                "edges": [
                    {"id": "e1", "source": "start-1", "target": "frappe-list-1"},
                    {"id": "e2", "source": "frappe-list-1", "target": "writer-1"},
                    {"id": "e3", "source": "writer-1", "target": "http-1"},
                    {"id": "e4", "source": "http-1", "target": "end-1"}
                ]
            }),
            "execution_count": 56,
            "last_executed_at": add_days(now(), -1)
        }
    ]
    
    created_workflows = []
    
    for workflow_data in workflows:
        try:
            # Check if workflow already exists
            if frappe.db.exists("Automesh Workflow", workflow_data["title"]):
                print(f"Workflow '{workflow_data['title']}' already exists, skipping...")
                continue
            
            # Create workflow
            workflow = frappe.new_doc("Automesh Workflow")
            workflow.title = workflow_data["title"]
            workflow.description = workflow_data["description"]
            workflow.version = workflow_data["version"]
            workflow.is_active = workflow_data["is_active"]
            workflow.tags = workflow_data["tags"]
            workflow.workflow_json = workflow_data["workflow_json"]
            workflow.execution_count = workflow_data["execution_count"]
            workflow.last_executed_at = workflow_data["last_executed_at"]
            workflow.created_at = add_days(now(), -30)  # Created 30 days ago
            workflow.updated_at = add_days(now(), -5)   # Updated 5 days ago
            workflow.created_by = frappe.session.user
            
            workflow.insert(ignore_permissions=True)
            created_workflows.append(workflow.title)
            print(f"✅ Created workflow: {workflow.title}")
            
        except Exception as e:
            print(f"❌ Error creating workflow '{workflow_data['title']}': {str(e)}")
            frappe.log_error(f"Error creating dummy workflow: {str(e)}")
    
    frappe.db.commit()
    
    print(f"\n✅ Successfully created {len(created_workflows)} workflows")
    print(f"Total workflows in database: {frappe.db.count('Automesh Workflow')}")
    
    return created_workflows


def execute():
    """Execute the dummy data creation"""
    print("=" * 60)
    print("Creating Dummy Workflows for Phase 1 Testing")
    print("=" * 60)
    
    created = create_dummy_workflows()
    
    print("\n" + "=" * 60)
    print("Dummy Data Creation Complete!")
    print("=" * 60)
    
    return created


if __name__ == "__main__":
    execute()
