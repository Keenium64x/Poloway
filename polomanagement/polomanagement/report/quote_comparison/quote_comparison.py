import frappe


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = [
		{"label": "Quote", "fieldname": "name", "fieldtype": "Link", "options": "Vendor Quote", "width": 140},
		{"label": "Title", "fieldname": "quote_title", "fieldtype": "Data", "width": 220},
		{"label": "Vendor", "fieldname": "vendor", "fieldtype": "Link", "options": "Vendor", "width": 160},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": "Quote Date", "fieldname": "quote_date", "fieldtype": "Date", "width": 110},
		{"label": "Valid Until", "fieldname": "valid_until", "fieldtype": "Date", "width": 110},
		{"label": "Horse", "fieldname": "linked_horse", "fieldtype": "Link", "options": "Horse", "width": 140},
		{"label": "Tournament", "fieldname": "tournament", "fieldtype": "Data", "width": 160},
		{"label": "Total", "fieldname": "total_amount", "fieldtype": "Currency", "width": 120},
		{"label": "File", "fieldname": "quote_file", "fieldtype": "Link", "options": "File", "width": 140},
	]
	return columns, get_data(filters)


def get_data(filters):
	conditions = {}
	if filters.vendor:
		conditions["vendor"] = filters.vendor
	if filters.status:
		conditions["status"] = filters.status
	if filters.linked_horse:
		conditions["linked_horse"] = filters.linked_horse
	if filters.tournament:
		conditions["tournament"] = ["like", f"%{filters.tournament}%"]

	return frappe.get_all(
		"Vendor Quote",
		filters=conditions,
		fields=[
			"name",
			"quote_title",
			"vendor",
			"status",
			"quote_date",
			"valid_until",
			"linked_horse",
			"tournament",
			"total_amount",
			"quote_file",
		],
		order_by="status asc, total_amount asc, quote_date desc",
	)
