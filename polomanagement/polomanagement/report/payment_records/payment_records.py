import frappe


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = [
		{"label": "Payment", "fieldname": "name", "fieldtype": "Link", "options": "Payment Record", "width": 140},
		{"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
		{"label": "Direction", "fieldname": "direction", "fieldtype": "Data", "width": 100},
		{"label": "Type", "fieldname": "transaction_type", "fieldtype": "Data", "width": 100},
		{"label": "Category", "fieldname": "transaction_category", "fieldtype": "Data", "width": 140},
		{"label": "Vendor", "fieldname": "vendor", "fieldtype": "Link", "options": "Vendor", "width": 160},
		{"label": "Owner", "fieldname": "horse_owner", "fieldtype": "Link", "options": "Horse Owner", "width": 160},
		{"label": "Amount", "fieldname": "total_amount", "fieldtype": "Currency", "width": 120},
		{"label": "Method", "fieldname": "payment_method", "fieldtype": "Data", "width": 120},
		{"label": "Receipt", "fieldname": "receipt_file", "fieldtype": "Link", "options": "File", "width": 150},
		{"label": "Source", "fieldname": "source_transaction", "fieldtype": "Link", "options": "Transaction Input", "width": 140},
	]
	return columns, get_data(filters)


def get_data(filters):
	conditions = {"docstatus": 1}
	if filters.direction:
		conditions["direction"] = filters.direction
	if filters.transaction_category:
		conditions["transaction_category"] = filters.transaction_category
	if filters.vendor:
		conditions["vendor"] = filters.vendor
	if filters.from_date and filters.to_date:
		conditions["posting_date"] = ["between", [filters.from_date, filters.to_date]]
	elif filters.from_date:
		conditions["posting_date"] = [">=", filters.from_date]
	elif filters.to_date:
		conditions["posting_date"] = ["<=", filters.to_date]

	rows = frappe.get_all(
		"Payment Record",
		filters=conditions,
		fields=[
			"name",
			"posting_date",
			"direction",
			"transaction_type",
			"transaction_category",
			"vendor",
			"horse_owner",
			"total_amount",
			"payment_method",
			"receipt_file",
			"source_transaction",
		],
		order_by="posting_date desc, creation desc",
	)

	if filters.horse:
		payment_names = [row.name for row in rows]
		if not payment_names:
			return []
		matching = set(frappe.get_all(
			"Payment Record Line",
			filters={"parent": ["in", payment_names], "horse": filters.horse},
			pluck="parent",
		))
		rows = [row for row in rows if row.name in matching]

	return rows
