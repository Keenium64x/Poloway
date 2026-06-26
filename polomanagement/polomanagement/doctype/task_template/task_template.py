import frappe
from frappe.model.document import Document
from polomanagement.polomanagement.doctype.item.item import validate_food_item


class TaskTemplate(Document):
	def validate(self):
		self.validate_items()

	def validate_items(self):
		for item in self.items:
			if item.ends_at and item.starts_at and item.ends_at < item.starts_at:
				frappe.throw(f"End time cannot be before start time in row {item.idx}.")
			if item.task_type == "Feeding":
				validate_food_item(item.feed_item)
