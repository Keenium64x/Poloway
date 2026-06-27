import frappe


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = [
		{"label": "Transaction", "fieldname": "name", "fieldtype": "Link", "options": "Transaction Input", "width": 150},
		{"label": "Date", "fieldname": "transaction_date", "fieldtype": "Date", "width": 110},
		{"label": "Type", "fieldname": "transaction_type", "fieldtype": "Data", "width": 100},
		{"label": "Category", "fieldname": "transaction_category", "fieldtype": "Data", "width": 140},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": "Party Type", "fieldname": "party_type", "fieldtype": "Data", "width": 110},
		{"label": "Party", "fieldname": "party_display", "fieldtype": "Data", "width": 180},
		{"label": "Vendor", "fieldname": "vendor", "fieldtype": "Link", "options": "Vendor", "width": 160},
		{"label": "Owner", "fieldname": "horse_owner", "fieldtype": "Link", "options": "Horse Owner", "width": 160},
		{"label": "Groom", "fieldname": "groom_profile", "fieldtype": "Link", "options": "Groom Profile", "width": 160},
		{"label": "Quote", "fieldname": "selected_quote", "fieldtype": "Link", "options": "Vendor Quote", "width": 140},
		{"label": "Amount", "fieldname": "total_amount", "fieldtype": "Currency", "width": 120},
		{"label": "Receipt", "fieldname": "receipt_file", "fieldtype": "Link", "options": "File", "width": 140},
	]
	return columns, get_data(filters)


def get_data(filters):
	conditions = {"docstatus": 0}
	if filters.status:
		conditions["status"] = filters.status
	else:
		conditions["status"] = ["!=", "Posted"]
	if filters.vendor:
		conditions["vendor"] = filters.vendor
	if filters.horse_owner:
		conditions["horse_owner"] = filters.horse_owner
	if filters.groom_profile:
		conditions["groom_profile"] = filters.groom_profile

	rows = frappe.get_all(
		"Transaction Input",
		filters=conditions,
		fields=[
			"name",
			"transaction_date",
			"transaction_type",
			"transaction_category",
			"status",
			"party_type",
			"vendor",
			"horse_owner",
			"groom_profile",
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

	for row in rows:
		row.party_display = get_party_display(row)

	return rows


def get_party_display(row):
	return row.vendor or row.horse_owner or row.groom_profile or row.party_type
