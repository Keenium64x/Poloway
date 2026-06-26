import frappe


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = [
		{"label": "Transaction", "fieldname": "name", "fieldtype": "Link", "options": "Transaction Input", "width": 150},
		{"label": "Date", "fieldname": "transaction_date", "fieldtype": "Date", "width": 110},
		{"label": "Type", "fieldname": "transaction_type", "fieldtype": "Data", "width": 100},
		{"label": "Category", "fieldname": "transaction_category", "fieldtype": "Data", "width": 140},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": "Vendor", "fieldname": "vendor", "fieldtype": "Link", "options": "Vendor", "width": 160},
		{"label": "Quote", "fieldname": "selected_quote", "fieldtype": "Link", "options": "Vendor Quote", "width": 140},
		{"label": "Amount", "fieldname": "total_amount", "fieldtype": "Currency", "width": 120},
		{"label": "Receipt", "fieldname": "receipt_file", "fieldtype": "Link", "options": "File", "width": 140},
	]
	return columns, get_data(filters)


def get_data(filters):
	conditions = {"payment_record": ["is", "not set"]}
	if filters.status:
		conditions["status"] = filters.status
	else:
		conditions["status"] = ["!=", "Posted"]
	if filters.vendor:
		conditions["vendor"] = filters.vendor

	rows = frappe.get_all(
		"Transaction Input",
		filters=conditions,
		fields=[
			"name",
			"transaction_date",
			"transaction_type",
			"transaction_category",
			"status",
			"vendor",
			"selected_quote",
			"total_amount",
			"receipt_file",
		],
		order_by="transaction_date desc, creation desc",
	)

	if filters.horse:
		names = [row.name for row in rows]
		if not names:
			return []
		matching = set(frappe.get_all(
			"Transaction Input Line",
			filters={"parent": ["in", names], "horse": filters.horse},
			pluck="parent",
		))
		rows = [row for row in rows if row.name in matching]

	return rows
