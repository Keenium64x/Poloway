import frappe


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = [
		{"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
		{"label": "Time", "fieldname": "posting_time", "fieldtype": "Time", "width": 90},
		{"label": "Item", "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 150},
		{"label": "Movement", "fieldname": "movement_type", "fieldtype": "Data", "width": 130},
		{"label": "Qty Change", "fieldname": "quantity_change", "fieldtype": "Float", "width": 100},
		{"label": "Qty After", "fieldname": "quantity_after", "fieldtype": "Float", "width": 100},
		{"label": "Rate", "fieldname": "valuation_rate", "fieldtype": "Currency", "width": 110},
		{"label": "Value Change", "fieldname": "value_change", "fieldtype": "Currency", "width": 120},
		{"label": "Value After", "fieldname": "value_after", "fieldtype": "Currency", "width": 120},
		{"label": "Voucher Type", "fieldname": "voucher_type", "fieldtype": "Link", "options": "DocType", "width": 130},
		{"label": "Voucher", "fieldname": "voucher_no", "fieldtype": "Dynamic Link", "options": "voucher_type", "width": 140},
		{"label": "Location", "fieldname": "inventory_location", "fieldtype": "Link", "options": "Inventory Location", "width": 150},
	]
	return columns, get_data(filters)


def get_data(filters):
	conditions = {}
	if filters.item:
		conditions["item"] = filters.item
	if filters.movement_type:
		conditions["movement_type"] = filters.movement_type
	if filters.inventory_location:
		conditions["inventory_location"] = filters.inventory_location
	if filters.from_date and filters.to_date:
		conditions["posting_date"] = ["between", [filters.from_date, filters.to_date]]
	elif filters.from_date:
		conditions["posting_date"] = [">=", filters.from_date]
	elif filters.to_date:
		conditions["posting_date"] = ["<=", filters.to_date]

	return frappe.get_all(
		"Item Stock Ledger",
		filters=conditions,
		fields=[
			"posting_date",
			"posting_time",
			"item",
			"movement_type",
			"quantity_change",
			"quantity_after",
			"valuation_rate",
			"value_change",
			"value_after",
			"voucher_type",
			"voucher_no",
			"inventory_location",
		],
		order_by="posting_date desc, posting_time desc, creation desc",
	)

