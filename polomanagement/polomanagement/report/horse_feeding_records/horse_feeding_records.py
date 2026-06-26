import frappe


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = [
		{"label": "Record", "fieldname": "name", "fieldtype": "Link", "options": "Horse Feeding Record", "width": 160},
		{"label": "Date", "fieldname": "feeding_date", "fieldtype": "Date", "width": 110},
		{"label": "Time", "fieldname": "feeding_time", "fieldtype": "Time", "width": 100},
		{"label": "Horse", "fieldname": "horse", "fieldtype": "Link", "options": "Horse", "width": 160},
		{"label": "Item", "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 180},
		{"label": "Quantity", "fieldname": "quantity", "fieldtype": "Float", "width": 100},
		{"label": "Unit", "fieldname": "unit", "fieldtype": "Data", "width": 80},
		{"label": "Responsible Person", "fieldname": "responsible_person", "fieldtype": "Link", "options": "User", "width": 180},
		{"label": "Instructions", "fieldname": "instructions", "fieldtype": "Data", "width": 260},
	]
	return columns, get_data(filters)


def get_data(filters):
	conditions = {}
	if filters.horse:
		conditions["horse"] = filters.horse

	return frappe.get_all(
		"Horse Feeding Record",
		filters=conditions,
		fields=["name", "feeding_date", "feeding_time", "horse", "item", "quantity", "unit", "responsible_person", "instructions"],
		order_by="feeding_date desc, feeding_time desc, creation desc",
	)
