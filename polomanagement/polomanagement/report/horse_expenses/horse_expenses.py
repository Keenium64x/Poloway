import frappe


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = [
		{"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
		{"label": "Transaction", "fieldname": "transaction_input", "fieldtype": "Link", "options": "Transaction Input", "width": 140},
		{"label": "Horse", "fieldname": "horse", "fieldtype": "Link", "options": "Horse", "width": 150},
		{"label": "Category", "fieldname": "transaction_category", "fieldtype": "Data", "width": 130},
		{"label": "Vendor", "fieldname": "vendor", "fieldtype": "Link", "options": "Vendor", "width": 160},
		{"label": "Description", "fieldname": "description", "fieldtype": "Data", "width": 240},
		{"label": "Quantity", "fieldname": "quantity", "fieldtype": "Float", "width": 90},
		{"label": "Rate", "fieldname": "rate", "fieldtype": "Currency", "width": 110},
		{"label": "Tax", "fieldname": "tax_amount", "fieldtype": "Currency", "width": 100},
		{"label": "Amount", "fieldname": "total", "fieldtype": "Currency", "width": 120},
		{"label": "Receipt", "fieldname": "receipt_file", "fieldtype": "Link", "options": "File", "width": 140},
	]
	return columns, get_data(filters)


def get_data(filters):
	conditions = ["tx.docstatus = 1", "line.horse is not null", "line.horse != ''"]
	values = {}

	if filters.horse:
		conditions.append("line.horse = %(horse)s")
		values["horse"] = filters.horse
	if filters.vendor:
		conditions.append("tx.vendor = %(vendor)s")
		values["vendor"] = filters.vendor
	if filters.transaction_category:
		conditions.append("coalesce(line.cost_category, tx.transaction_category, 'Other') = %(transaction_category)s")
		values["transaction_category"] = filters.transaction_category
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
			line.horse,
			coalesce(line.cost_category, tx.transaction_category, 'Other') as transaction_category,
			tx.vendor,
			line.description,
			line.quantity,
			line.rate,
			line.tax_amount,
			case when tx.direction = 'Money In' then line.total * -1 else line.total end as total,
			tx.receipt_file
		from `tabTransaction Input Line` line
		inner join `tabTransaction Input` tx on tx.name = line.parent
		where {" and ".join(conditions)}
		order by tx.transaction_date desc, tx.creation desc, line.idx asc
		""",
		values,
		as_dict=True,
	)
