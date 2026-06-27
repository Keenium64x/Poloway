import frappe


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = [
		{"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
		{"label": "Transaction", "fieldname": "transaction_input", "fieldtype": "Link", "options": "Transaction Input", "width": 140},
		{"label": "Item", "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 150},
		{"label": "Direction", "fieldname": "direction", "fieldtype": "Data", "width": 100},
		{"label": "Vendor", "fieldname": "vendor", "fieldtype": "Link", "options": "Vendor", "width": 160},
		{"label": "Quantity", "fieldname": "quantity", "fieldtype": "Float", "width": 90},
		{"label": "Unit", "fieldname": "unit", "fieldtype": "Data", "width": 80},
		{"label": "Rate", "fieldname": "rate", "fieldtype": "Currency", "width": 110},
		{"label": "Tax", "fieldname": "tax_amount", "fieldtype": "Currency", "width": 100},
		{"label": "Total", "fieldname": "total", "fieldtype": "Currency", "width": 120},
		{"label": "Receipt", "fieldname": "receipt_file", "fieldtype": "Link", "options": "File", "width": 140},
	]
	return columns, get_data(filters)


def get_data(filters):
	conditions = ["tx.docstatus = 1", "line.item is not null", "line.item != ''"]
	values = {}

	if filters.item:
		conditions.append("line.item = %(item)s")
		values["item"] = filters.item
	if filters.vendor:
		conditions.append("tx.vendor = %(vendor)s")
		values["vendor"] = filters.vendor
	if filters.from_date:
		conditions.append("tx.transaction_date >= %(from_date)s")
		values["from_date"] = filters.from_date
	if filters.to_date:
		conditions.append("tx.transaction_date <= %(to_date)s")
		values["to_date"] = filters.to_date

	return frappe.db.sql(
		f"""
		select
			tx.transaction_date as posting_date,
			tx.name as transaction_input,
			line.item,
			tx.direction,
			tx.vendor,
			line.quantity,
			line.unit,
			line.rate,
			line.tax_amount,
			line.total,
			tx.receipt_file
		from `tabTransaction Input Line` line
		inner join `tabTransaction Input` tx on tx.name = line.parent
		where {" and ".join(conditions)}
		order by tx.transaction_date desc, tx.creation desc, line.idx asc
		""",
		values,
		as_dict=True,
	)
