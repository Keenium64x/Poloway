import frappe
from frappe.model.document import Document


class TaskTemplate(Document):
	def validate(self):
		self.validate_items()

	def validate_items(self):
		for item in self.items:
			if item.ends_at and item.starts_at and item.ends_at < item.starts_at:
				frappe.throw(f"End time cannot be before start time in row {item.idx}.")

