import frappe


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = [
		{"label": "Record", "fieldname": "name", "fieldtype": "Link", "options": "Horse Medical Record", "width": 160},
		{"label": "Date", "fieldname": "record_date", "fieldtype": "Date", "width": 110},
		{"label": "Horse", "fieldname": "horse", "fieldtype": "Link", "options": "Horse", "width": 160},
		{"label": "Type", "fieldname": "record_type", "fieldtype": "Data", "width": 130},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 130},
		{"label": "Responsible Person", "fieldname": "responsible_person", "fieldtype": "Link", "options": "User", "width": 180},
		{"label": "Summary", "fieldname": "summary", "fieldtype": "Data", "width": 280},
		{"label": "Next Due", "fieldname": "next_due_date", "fieldtype": "Date", "width": 110},
	]
	return columns, get_data(filters)


def get_data(filters):
	conditions = {}
	if filters.horse:
		conditions["horse"] = filters.horse

	return frappe.get_all(
		"Horse Medical Record",
		filters=conditions,
		fields=["name", "record_date", "horse", "record_type", "status", "responsible_person", "summary", "next_due_date"],
		order_by="record_date desc, creation desc",
	)
