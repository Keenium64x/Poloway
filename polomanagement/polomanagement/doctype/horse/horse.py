# Copyright (c) 2026, Keenan Solomon and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class Horse(Document):
	def validate(self):
		self.validate_ownership_percentage()

	def validate_ownership_percentage(self):
		total_percentage = sum(flt(row.percentage) for row in self.get("ownership") or [])
		if total_percentage and flt(total_percentage, 2) != 100:
			frappe.throw("Ownership percentage must add up to 100%.")
