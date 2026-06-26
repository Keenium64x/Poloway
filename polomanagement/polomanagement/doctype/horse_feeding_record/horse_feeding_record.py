# Copyright (c) 2026, Keenan Solomon and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from polomanagement.polomanagement.doctype.item.item import validate_food_item


class HorseFeedingRecord(Document):
	def validate(self):
		self.validate_food_item()

	def validate_food_item(self):
		if not self.item:
			return

		validate_food_item(self.item)
