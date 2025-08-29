import frappe
from frappe.permissions import add_permission, update_permission_property

def setup_permissions():
    """Setup role-based permissions for all Automesh DocTypes"""
    
    # Define roles for the system
    roles = [
        {"role_name": "Automesh Admin", "desk_access": 1, "two_factor_auth": 0},
        {"role_name": "Automesh User", "desk_access": 1, "two_factor_auth": 0}
    ]
    
    # Create roles if they don't exist
    for role in roles:
        if not frappe.db.exists("Role", role["role_name"]):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role["role_name"],
                "desk_access": role["desk_access"],
                "two_factor_auth": role["two_factor_auth"]
            }).insert(ignore_permissions=True)
            print(f"Created role: {role['role_name']}")
    
    # Define permissions for each DocType
    permissions = [
        # Automesh Workflow
        {
            "doctype": "Automesh Workflow",
            "role": "Automesh Admin",
            "permissions": {
                "read": 1, "write": 1, "create": 1, "delete": 1, 
                "submit": 0, "cancel": 0, "amend": 0, 
                "print": 1, "email": 1, "report": 1, "import": 1, "export": 1, 
                "set_user_permissions": 1, "share": 1
            }
        },
        {
            "doctype": "Automesh Workflow",
            "role": "Automesh User",
            "permissions": {
                "read": 1, "write": 1, "create": 1, "delete": 0, 
                "submit": 0, "cancel": 0, "amend": 0, 
                "print": 1, "email": 1, "report": 1, "import": 0, "export": 1, 
                "set_user_permissions": 0, "share": 1
            }
        },
        
        # Automesh Node Type
        {
            "doctype": "Automesh Node Type",
            "role": "Automesh Admin",
            "permissions": {
                "read": 1, "write": 1, "create": 1, "delete": 1, 
                "submit": 0, "cancel": 0, "amend": 0, 
                "print": 1, "email": 1, "report": 1, "import": 1, "export": 1, 
                "set_user_permissions": 1, "share": 1
            }
        },
        {
            "doctype": "Automesh Node Type",
            "role": "Automesh User",
            "permissions": {
                "read": 1, "write": 0, "create": 0, "delete": 0, 
                "submit": 0, "cancel": 0, "amend": 0, 
                "print": 1, "email": 1, "report": 1, "import": 0, "export": 1, 
                "set_user_permissions": 0, "share": 0
            }
        },
        
        # Automesh Execution
        {
            "doctype": "Automesh Execution",
            "role": "Automesh Admin",
            "permissions": {
                "read": 1, "write": 1, "create": 1, "delete": 1, 
                "submit": 0, "cancel": 0, "amend": 0, 
                "print": 1, "email": 1, "report": 1, "import": 0, "export": 1, 
                "set_user_permissions": 1, "share": 1
            }
        },
        {
            "doctype": "Automesh Execution",
            "role": "Automesh User",
            "permissions": {
                "read": 1, "write": 0, "create": 1, "delete": 0, 
                "submit": 0, "cancel": 0, "amend": 0, 
                "print": 1, "email": 1, "report": 1, "import": 0, "export": 1, 
                "set_user_permissions": 0, "share": 0
            }
        },
        
        # Automesh Node Execution
        {
            "doctype": "Automesh Node Execution",
            "role": "Automesh Admin",
            "permissions": {
                "read": 1, "write": 1, "create": 1, "delete": 1, 
                "submit": 0, "cancel": 0, "amend": 0, 
                "print": 1, "email": 1, "report": 1, "import": 0, "export": 1, 
                "set_user_permissions": 1, "share": 1
            }
        },
        {
            "doctype": "Automesh Node Execution",
            "role": "Automesh User",
            "permissions": {
                "read": 1, "write": 0, "create": 0, "delete": 0, 
                "submit": 0, "cancel": 0, "amend": 0, 
                "print": 1, "email": 1, "report": 1, "import": 0, "export": 1, 
                "set_user_permissions": 0, "share": 0
            }
        },
        
        # Automesh Template
        {
            "doctype": "Automesh Template",
            "role": "Automesh Admin",
            "permissions": {
                "read": 1, "write": 1, "create": 1, "delete": 1, 
                "submit": 0, "cancel": 0, "amend": 0, 
                "print": 1, "email": 1, "report": 1, "import": 1, "export": 1, 
                "set_user_permissions": 1, "share": 1
            }
        },
        {
            "doctype": "Automesh Template",
            "role": "Automesh User",
            "permissions": {
                "read": 1, "write": 0, "create": 0, "delete": 0, 
                "submit": 0, "cancel": 0, "amend": 0, 
                "print": 1, "email": 1, "report": 1, "import": 0, "export": 1, 
                "set_user_permissions": 0, "share": 0
            }
        },
        
        # Child DocTypes
        # (Permissions are inherited from parent, but we set them explicitly for clarity)
        
        # Automesh Variable
        {
            "doctype": "Automesh Variable",
            "role": "Automesh Admin",
            "permissions": {
                "read": 1, "write": 1, "create": 1, "delete": 1, 
                "submit": 0, "cancel": 0, "amend": 0, 
                "print": 1, "email": 1, "report": 1, "import": 0, "export": 1, 
                "set_user_permissions": 0, "share": 0
            }
        },
        {
            "doctype": "Automesh Variable",
            "role": "Automesh User",
            "permissions": {
                "read": 1, "write": 1, "create": 1, "delete": 1, 
                "submit": 0, "cancel": 0, "amend": 0, 
                "print": 1, "email": 1, "report": 1, "import": 0, "export": 1, 
                "set_user_permissions": 0, "share": 0
            }
        },
        
        # Automesh Connection
        {
            "doctype": "Automesh Connection",
            "role": "Automesh Admin",
            "permissions": {
                "read": 1, "write": 1, "create": 1, "delete": 1, 
                "submit": 0, "cancel": 0, "amend": 0, 
                "print": 1, "email": 1, "report": 1, "import": 0, "export": 1, 
                "set_user_permissions": 0, "share": 0
            }
        },
        {
            "doctype": "Automesh Connection",
            "role": "Automesh User",
            "permissions": {
                "read": 1, "write": 1, "create": 1, "delete": 1, 
                "submit": 0, "cancel": 0, "amend": 0, 
                "print": 1, "email": 1, "report": 1, "import": 0, "export": 1, 
                "set_user_permissions": 0, "share": 0
            }
        }
    ]
    
    # Apply permissions
    for perm in permissions:
        doctype = perm["doctype"]
        role = perm["role"]
        
        # Check if permission exists
        permission_exists = frappe.db.exists(
            "Custom DocPerm", 
            {"parent": doctype, "role": role}
        )
        
        if not permission_exists:
            # Add permission if it doesn't exist
            add_permission(doctype, role, 0)
            print(f"Added permission for {role} on {doctype}")
        
        # Update permission properties
        for prop, value in perm["permissions"].items():
            update_permission_property(doctype, role, 0, prop, value)
            
        print(f"Updated permissions for {role} on {doctype}")
    
    print("Permissions setup complete")

def create_user_types():
    """Create user types for Automesh"""
    
    # Define user types
    user_types = [
        {
            "name": "Automesh Admin",
            "role": "Automesh Admin",
            "description": "Administrator with full access to Automesh system",
            "user_doctypes": [
                {"document_type": "Automesh Workflow", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "import": 1, "export": 1, "print": 1, "email": 1, "report": 1, "share": 1},
                {"document_type": "Automesh Node Type", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "import": 1, "export": 1, "print": 1, "email": 1, "report": 1, "share": 1},
                {"document_type": "Automesh Execution", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "import": 0, "export": 1, "print": 1, "email": 1, "report": 1, "share": 1},
                {"document_type": "Automesh Template", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "cancel": 0, "amend": 0, "import": 1, "export": 1, "print": 1, "email": 1, "report": 1, "share": 1}
            ]
        },
        {
            "name": "Automesh User",
            "role": "Automesh User",
            "description": "Regular user with restricted access to Automesh system",
            "user_doctypes": [
                {"document_type": "Automesh Workflow", "read": 1, "write": 1, "create": 1, "delete": 0, "submit": 0, "cancel": 0, "amend": 0, "import": 0, "export": 1, "print": 1, "email": 1, "report": 1, "share": 1},
                {"document_type": "Automesh Node Type", "read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0, "amend": 0, "import": 0, "export": 1, "print": 1, "email": 1, "report": 1, "share": 0},
                {"document_type": "Automesh Execution", "read": 1, "write": 0, "create": 1, "delete": 0, "submit": 0, "cancel": 0, "amend": 0, "import": 0, "export": 1, "print": 1, "email": 1, "report": 1, "share": 0},
                {"document_type": "Automesh Template", "read": 1, "write": 0, "create": 0, "delete": 0, "submit": 0, "cancel": 0, "amend": 0, "import": 0, "export": 1, "print": 1, "email": 1, "report": 1, "share": 0}
            ]
        }
    ]
    
    # Create user types
    for user_type in user_types:
        if not frappe.db.exists("User Type", user_type["name"]):
            doc = frappe.new_doc("User Type")
            doc.name = user_type["name"]
            doc.role = user_type["role"]
            doc.description = user_type["description"]
            
            for doctype_perm in user_type["user_doctypes"]:
                doc.append("user_doctypes", doctype_perm)
                
            doc.insert(ignore_permissions=True)
            print(f"Created user type: {user_type['name']}")
        else:
            print(f"User type {user_type['name']} already exists")
    
    print("User types setup complete")

# Add a function to run the entire setup
def setup():
    """Run the entire permissions setup"""
    setup_permissions()
    create_user_types()
    print("Automesh permissions and user types setup complete")

# Execute the setup if running directly
if __name__ == "__main__":
    setup()
