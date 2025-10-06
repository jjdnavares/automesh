"""
Add database indexes for performance optimization
Phase 3.1.1 - Backend Performance
"""

import frappe


def execute():
    """Add indexes to Automesh Workflow and Automesh Execution tables"""
    
    # Add indexes to Automesh Workflow
    add_workflow_indexes()
    
    # Add indexes to Automesh Execution
    add_execution_indexes()
    
    frappe.db.commit()


def add_workflow_indexes():
    """Add indexes to Automesh Workflow table"""
    
    indexes = [
        # Single column indexes
        ("tabAutomesh Workflow", "is_active", "idx_is_active"),
        ("tabAutomesh Workflow", "created_by", "idx_created_by"),
        ("tabAutomesh Workflow", "updated_at", "idx_updated_at"),
        ("tabAutomesh Workflow", "created_at", "idx_created_at"),
        ("tabAutomesh Workflow", "last_executed_at", "idx_last_executed_at"),
        ("tabAutomesh Workflow", "title", "idx_title"),
        
        # Composite indexes
        ("tabAutomesh Workflow", ["created_by", "is_active"], "idx_created_by_is_active"),
    ]
    
    for index_def in indexes:
        try:
            if isinstance(index_def[1], list):
                # Composite index
                table, columns, index_name = index_def
                
                # Check if index exists
                existing = frappe.db.sql(f"""
                    SELECT COUNT(*) as count 
                    FROM information_schema.statistics 
                    WHERE table_schema = DATABASE()
                    AND table_name = '{table}'
                    AND index_name = '{index_name}'
                """, as_dict=True)
                
                if not existing[0].count:
                    columns_str = ", ".join(columns)
                    frappe.db.sql(f"""
                        ALTER TABLE `{table}` 
                        ADD INDEX {index_name} ({columns_str})
                    """)
                    print(f"✓ Added composite index {index_name} on {table}")
                else:
                    print(f"⊙ Index {index_name} already exists on {table}")
            else:
                # Single column index
                table, column, index_name = index_def
                
                # Check if index exists
                existing = frappe.db.sql(f"""
                    SELECT COUNT(*) as count 
                    FROM information_schema.statistics 
                    WHERE table_schema = DATABASE()
                    AND table_name = '{table}'
                    AND index_name = '{index_name}'
                """, as_dict=True)
                
                if not existing[0].count:
                    frappe.db.sql(f"""
                        ALTER TABLE `{table}` 
                        ADD INDEX {index_name} ({column})
                    """)
                    print(f"✓ Added index {index_name} on {table}.{column}")
                else:
                    print(f"⊙ Index {index_name} already exists on {table}")
        except Exception as e:
            # Index might already exist or other error
            print(f"⚠ Could not add index {index_def}: {str(e)}")


def add_execution_indexes():
    """Add indexes to Automesh Execution table"""
    
    indexes = [
        # Single column indexes
        ("tabAutomesh Execution", "workflow", "idx_workflow"),
        ("tabAutomesh Execution", "status", "idx_status"),
        ("tabAutomesh Execution", "start_time", "idx_start_time"),
        ("tabAutomesh Execution", "created_by", "idx_created_by"),
        
        # Composite indexes
        ("tabAutomesh Execution", ["workflow", "start_time"], "idx_workflow_start_time"),
        ("tabAutomesh Execution", ["start_time", "status"], "idx_start_time_status"),
    ]
    
    for index_def in indexes:
        try:
            if isinstance(index_def[1], list):
                # Composite index
                table, columns, index_name = index_def
                
                # Check if index exists
                existing = frappe.db.sql(f"""
                    SELECT COUNT(*) as count 
                    FROM information_schema.statistics 
                    WHERE table_schema = DATABASE()
                    AND table_name = '{table}'
                    AND index_name = '{index_name}'
                """, as_dict=True)
                
                if not existing[0].count:
                    columns_str = ", ".join(columns)
                    frappe.db.sql(f"""
                        ALTER TABLE `{table}` 
                        ADD INDEX {index_name} ({columns_str})
                    """)
                    print(f"✓ Added composite index {index_name} on {table}")
                else:
                    print(f"⊙ Index {index_name} already exists on {table}")
            else:
                # Single column index
                table, column, index_name = index_def
                
                # Check if index exists
                existing = frappe.db.sql(f"""
                    SELECT COUNT(*) as count 
                    FROM information_schema.statistics 
                    WHERE table_schema = DATABASE()
                    AND table_name = '{table}'
                    AND index_name = '{index_name}'
                """, as_dict=True)
                
                if not existing[0].count:
                    frappe.db.sql(f"""
                        ALTER TABLE `{table}` 
                        ADD INDEX {index_name} ({column})
                    """)
                    print(f"✓ Added index {index_name} on {table}.{column}")
                else:
                    print(f"⊙ Index {index_name} already exists on {table}")
        except Exception as e:
            # Index might already exist or other error
            print(f"⚠ Could not add index {index_def}: {str(e)}")
