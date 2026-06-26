import frappe
from frappe.tests import IntegrationTestCase


class IntegrationTestOwnerTask(IntegrationTestCase):
	def test_schedule_defaults(self):
		doc = frappe.get_doc({
			"doctype": "Owner Task",
			"subject": "Book tournament transport",
			"task_type": "Transport",
		})
		doc.insert(ignore_permissions=True)
		self.assertTrue(doc.due_date)
		self.assertTrue(doc.starts_on)
		self.assertTrue(doc.ends_on)
