# Copyright (c) 2025, jjdnavares and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class AutomeshWorkflowShare(Document):
	def validate(self):
		"""Validate the workflow share"""
		# Check for duplicate shares
		existing = frappe.db.exists(
			"Automesh Workflow Share",
			{
				"workflow": self.workflow,
				"shared_with": self.shared_with,
				"name": ["!=", self.name]
			}
		)
		
		if existing:
			frappe.throw(_("This workflow is already shared with this user"))
		
		# Validate permission level
		valid_permissions = ["view", "execute", "edit", "full"]
		if self.permission_level not in valid_permissions:
			frappe.throw(_("Invalid permission level"))
		
		# Check if user has permission to share
		if not self.is_new():
			return
			
		workflow = frappe.get_doc("Automesh Workflow", self.workflow)
		user = frappe.session.user
		
		# Only owner or system manager can share
		is_owner = workflow.created_by == user or workflow.owner == user
		is_admin = "System Manager" in frappe.get_roles(user)
		
		if not (is_owner or is_admin):
			frappe.throw(_("You don't have permission to share this workflow"))
