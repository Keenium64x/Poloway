# Copyright (c) 2026, Keenan Solomon and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class HorseFeedingRecord(Document):
	def validate(self):
		self.validate_food_item()

	def validate_food_item(self):
		if not self.item:
			return

		category = frappe.db.get_value("Horse Feed Item", self.item, "category")
		if category != "Food":
			frappe.throw("Feeding records can only use items in the Food category.")
