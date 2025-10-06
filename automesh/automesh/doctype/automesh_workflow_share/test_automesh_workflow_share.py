# Copyright (c) 2025, jjdnavares and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestAutomeshWorkflowShare(FrappeTestCase):
	def setUp(self):
		"""Set up test data"""
		# Create a test workflow
		if not frappe.db.exists("Automesh Workflow", "Test Workflow for Sharing"):
			workflow = frappe.get_doc({
				"doctype": "Automesh Workflow",
				"title": "Test Workflow for Sharing",
				"description": "Test workflow",
				"version": "1.0.0",
				"is_active": 1,
				"created_by": frappe.session.user
			})
			workflow.insert()
	
	def tearDown(self):
		"""Clean up test data"""
		# Delete test shares
		frappe.db.delete("Automesh Workflow Share", {
			"workflow": "Test Workflow for Sharing"
		})
		
		# Delete test workflow
		if frappe.db.exists("Automesh Workflow", "Test Workflow for Sharing"):
			frappe.delete_doc("Automesh Workflow", "Test Workflow for Sharing")
	
	def test_create_share(self):
		"""Test creating a workflow share"""
		share = frappe.get_doc({
			"doctype": "Automesh Workflow Share",
			"workflow": "Test Workflow for Sharing",
			"shared_with": "Administrator",
			"permission_level": "view",
			"shared_by": frappe.session.user,
			"is_active": 1
		})
		share.insert()
		
		self.assertTrue(frappe.db.exists("Automesh Workflow Share", share.name))
		self.assertEqual(share.permission_level, "view")
	
	def test_duplicate_share_validation(self):
		"""Test that duplicate shares are prevented"""
		# Create first share
		share1 = frappe.get_doc({
			"doctype": "Automesh Workflow Share",
			"workflow": "Test Workflow for Sharing",
			"shared_with": "Administrator",
			"permission_level": "view",
			"shared_by": frappe.session.user,
			"is_active": 1
		})
		share1.insert()
		
		# Try to create duplicate
		share2 = frappe.get_doc({
			"doctype": "Automesh Workflow Share",
			"workflow": "Test Workflow for Sharing",
			"shared_with": "Administrator",
			"permission_level": "edit",
			"shared_by": frappe.session.user,
			"is_active": 1
		})
		
		with self.assertRaises(frappe.ValidationError):
			share2.insert()
