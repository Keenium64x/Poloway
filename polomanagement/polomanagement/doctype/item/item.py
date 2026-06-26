# Copyright (c) 2026, Keenan Solomon and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class Item(Document):
	def validate(self):
		self.apply_category_defaults()
		self.total_value = flt(self.quantity_on_hand) * flt(self.valuation_rate)

	def apply_category_defaults(self):
		if not self.item_category:
			return

		defaults = get_item_category_defaults(self.item_category)
		applied_from = []

		for item_field, category_field in {
			"inventory_location": "default_inventory_location",
			"default_unit": "default_unit",
			"responsible_role": "default_responsible_role",
			"responsible_user": "default_responsible_user",
		}.items():
			if not self.get(item_field) and defaults.get(category_field):
				self.set(item_field, defaults.get(category_field))
				applied_from.append(item_field.replace("_", " ").title())

		if applied_from:
			self.assignment_source = _("Inherited from {0}").format(self.item_category)


def get_item_category_defaults(category):
	values = {}

	for category_name in get_category_lineage(category):
		row = frappe.db.get_value(
			"Item Category",
			category_name,
			[
				"category_type",
				"default_inventory_location",
				"default_unit",
				"default_responsible_role",
				"default_responsible_user",
			],
			as_dict=True,
		)
		if not row:
			continue

		for fieldname, value in row.items():
			if value and not values.get(fieldname):
				values[fieldname] = value

	return values


def get_category_lineage(category):
	lineage = []
	seen = set()
	current = category

	while current and current not in seen:
		seen.add(current)
		lineage.append(current)
		current = frappe.db.get_value("Item Category", current, "parent_item_category")

	return lineage


def is_food_item(item):
	category = frappe.db.get_value("Item", item, "item_category")
	if not category:
		return False

	for category_name in get_category_lineage(category):
		if frappe.db.get_value("Item Category", category_name, "category_type") == "Food":
			return True

	return False


def validate_food_item(item):
	if item and not is_food_item(item):
		frappe.throw(_("Feeding records can only use items in the Food category."))


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def food_item_query(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(
		"""
		select item.name, item.item_name
		from `tabItem` item
		inner join `tabItem Category` category on category.name = item.item_category
		inner join `tabItem Category` ancestor
			on ancestor.lft <= category.lft
			and ancestor.rgt >= category.rgt
			and ancestor.category_type = 'Food'
		where item.is_active = 1
			and (
				item.name like %(txt)s
				or item.item_name like %(txt)s
				or item.description like %(txt)s
			)
		order by item.item_name, item.name
		limit %(start)s, %(page_len)s
		""",
		{
			"txt": f"%{txt}%",
			"start": start,
			"page_len": page_len,
		},
	)
