# Copyright (c) 2026, Keenan Solomon and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils.nestedset import NestedSet


class ItemCategory(NestedSet):
	def validate(self):
		if self.parent_item_category and self.parent_item_category == self.name:
			frappe.throw(_("An item category cannot be its own parent."))
