"""
Test suite for Workflow API Performance Optimizations
Phase 3.1 - Backend Performance Tests
"""

import frappe
import unittest
import json
from frappe.utils import now, add_days
import time


class TestWorkflowAPIPerformance(unittest.TestCase):
    """Test performance optimizations in workflow API"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data"""
        frappe.set_user("Administrator")
        
        # Create test workflows
        cls.test_workflows = []
        for i in range(20):
            workflow = frappe.get_doc({
                "doctype": "Automesh Workflow",
                "title": f"Test Workflow {i}",
                "description": f"Test description for workflow {i}",
                "tags": f"test,automation,workflow{i % 3}",
                "version": "1.0.0",
                "is_active": i % 2 == 0,  # Alternate active/inactive
                "execution_count": i * 10,
                "created_at": add_days(now(), -i),
                "updated_at": add_days(now(), -i),
                "created_by": "Administrator",
                "workflow_json": json.dumps({
                    "nodes": [{"id": f"node_{j}", "type": "start"} for j in range(5)],
                    "edges": []
                })
            })
            workflow.insert()
            cls.test_workflows.append(workflow.name)
        
        # Create test executions
        for workflow_name in cls.test_workflows[:5]:
            for j in range(10):
                execution = frappe.get_doc({
                    "doctype": "Automesh Execution",
                    "workflow": workflow_name,
                    "status": "completed" if j % 2 == 0 else "failed",
                    "start_time": add_days(now(), -j),
                    "end_time": add_days(now(), -j),
                    "created_by": "Administrator"
                })
                execution.insert()
        
        frappe.db.commit()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        # Delete test executions
        frappe.db.sql("DELETE FROM `tabAutomesh Execution` WHERE workflow IN %s", 
                     (cls.test_workflows,))
        
        # Delete test workflows
        for workflow_name in cls.test_workflows:
            frappe.delete_doc("Automesh Workflow", workflow_name, force=True)
        
        frappe.db.commit()
    
    def test_get_workflows_performance(self):
        """Test that get_workflows completes in reasonable time"""
        from automesh.automesh.api.workflow import get_workflows
        
        start_time = time.time()
        result = get_workflows(limit=10, offset=0)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should complete in less than 1 second
        self.assertLess(execution_time, 1.0, 
                       f"get_workflows took {execution_time:.3f}s, expected < 1.0s")
        
        # Verify result structure
        self.assertIn("workflows", result)
        self.assertIn("total", result)
        self.assertIsInstance(result["workflows"], list)
    
    def test_get_workflows_with_search(self):
        """Test search performance at database level"""
        from automesh.automesh.api.workflow import get_workflows
        
        start_time = time.time()
        result = get_workflows(search="Workflow 1", limit=10)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Search should be fast
        self.assertLess(execution_time, 1.0,
                       f"Search took {execution_time:.3f}s, expected < 1.0s")
        
        # Verify search results
        self.assertGreater(len(result["workflows"]), 0)
        for workflow in result["workflows"]:
            self.assertIn("1", workflow["name"])
    
    def test_get_workflows_with_tags(self):
        """Test tag filtering performance"""
        from automesh.automesh.api.workflow import get_workflows
        
        start_time = time.time()
        result = get_workflows(tags="automation", limit=10)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Tag filtering should be fast
        self.assertLess(execution_time, 1.0,
                       f"Tag filtering took {execution_time:.3f}s, expected < 1.0s")
        
        # Verify tag filtering
        self.assertGreater(len(result["workflows"]), 0)
    
    def test_get_workflows_pagination(self):
        """Test pagination performance"""
        from automesh.automesh.api.workflow import get_workflows
        
        # Test first page
        start_time = time.time()
        page1 = get_workflows(limit=5, offset=0)
        end_time = time.time()
        
        execution_time = end_time - start_time
        self.assertLess(execution_time, 1.0)
        
        # Test second page
        page2 = get_workflows(limit=5, offset=5)
        
        # Pages should have different workflows
        page1_ids = [w["id"] for w in page1["workflows"]]
        page2_ids = [w["id"] for w in page2["workflows"]]
        
        # No overlap between pages
        self.assertEqual(len(set(page1_ids) & set(page2_ids)), 0)
    
    def test_get_workflow_statistics_performance(self):
        """Test statistics query performance"""
        from automesh.automesh.api.workflow import get_workflow_statistics
        
        start_time = time.time()
        result = get_workflow_statistics(days=7)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Statistics should complete quickly
        self.assertLess(execution_time, 1.0,
                       f"Statistics took {execution_time:.3f}s, expected < 1.0s")
        
        # Verify result structure
        self.assertIn("total_workflows", result)
        self.assertIn("active_workflows", result)
        self.assertIn("total_executions", result)
        self.assertIn("completed", result)
        self.assertIn("failed", result)
    
    def test_statistics_caching(self):
        """Test that statistics are cached properly"""
        from automesh.automesh.api.workflow import get_workflow_statistics
        
        # Clear cache
        cache_key = f"workflow_stats_Administrator_7"
        frappe.cache().delete_value(cache_key)
        
        # First call - should hit database
        start_time = time.time()
        result1 = get_workflow_statistics(days=7)
        first_call_time = time.time() - start_time
        
        # Second call - should hit cache
        start_time = time.time()
        result2 = get_workflow_statistics(days=7)
        second_call_time = time.time() - start_time
        
        # Cached call should be significantly faster
        self.assertLess(second_call_time, first_call_time / 2,
                       f"Cached call ({second_call_time:.3f}s) not faster than first call ({first_call_time:.3f}s)")
        
        # Results should be identical
        self.assertEqual(result1, result2)
    
    def test_bulk_operations_performance(self):
        """Test bulk delete performance"""
        from automesh.automesh.api.workflow import bulk_delete_workflows
        
        # Create temporary workflows for deletion
        temp_workflows = []
        for i in range(5):
            workflow = frappe.get_doc({
                "doctype": "Automesh Workflow",
                "title": f"Temp Workflow {i}",
                "description": "Temporary workflow for testing",
                "created_by": "Administrator",
                "workflow_json": json.dumps({"nodes": [], "edges": []})
            })
            workflow.insert()
            temp_workflows.append(workflow.name)
        
        frappe.db.commit()
        
        # Test bulk delete
        start_time = time.time()
        result = bulk_delete_workflows(workflow_ids=temp_workflows)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Bulk delete should be reasonably fast
        self.assertLess(execution_time, 2.0,
                       f"Bulk delete took {execution_time:.3f}s, expected < 2.0s")
        
        # Verify all were deleted
        self.assertEqual(result["deleted_count"], 5)
        self.assertEqual(result["failed_count"], 0)
    
    def test_workflow_json_loading(self):
        """Test that workflow_json is loaded efficiently"""
        from automesh.automesh.api.workflow import get_workflows
        
        # Get workflows with JSON data
        start_time = time.time()
        result = get_workflows(limit=10)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should load JSON efficiently in single query
        self.assertLess(execution_time, 1.0)
        
        # Verify JSON is loaded
        for workflow in result["workflows"]:
            self.assertIn("nodes", workflow)
            self.assertIn("edges", workflow)
            self.assertIsInstance(workflow["nodes"], list)
            self.assertIsInstance(workflow["edges"], list)
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        from automesh.automesh.api.workflow import get_workflows
        import threading
        
        results = []
        errors = []
        
        def fetch_workflows():
            try:
                result = get_workflows(limit=5)
                results.append(result)
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=fetch_workflows)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 5)


def run_tests():
    """Run all performance tests"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWorkflowAPIPerformance)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


if __name__ == "__main__":
    run_tests()
