import frappe
from frappe.utils import flt


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = [
		{"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 105},
		{"label": "Transaction", "fieldname": "transaction_input", "fieldtype": "Link", "options": "Transaction Input", "width": 135},
		{"label": "Account", "fieldname": "account", "fieldtype": "Link", "options": "Money Account", "width": 180},
		{"label": "Category", "fieldname": "transaction_category", "fieldtype": "Data", "width": 140},
		{"label": "Party", "fieldname": "party_display", "fieldtype": "Data", "width": 180},
		{"label": "Detail Type", "fieldname": "line_type", "fieldtype": "Data", "width": 100},
		{"label": "Horse", "fieldname": "horse", "fieldtype": "Link", "options": "Horse", "width": 130},
		{"label": "Groom", "fieldname": "groom_profile", "fieldtype": "Link", "options": "Groom Profile", "width": 130},
		{"label": "Item", "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 140},
		{"label": "Reference", "fieldname": "reference_display", "fieldtype": "Data", "width": 160},
		{"label": "Description", "fieldname": "description", "fieldtype": "Data", "width": 260},
		{"label": "Debit", "fieldname": "debit", "fieldtype": "Currency", "width": 115},
		{"label": "Credit", "fieldname": "credit", "fieldtype": "Currency", "width": 115},
		{"label": "Balance", "fieldname": "balance", "fieldtype": "Currency", "width": 120},
	]
	data = get_data(filters)
	return columns, data, None, get_chart(data), get_summary(data)


def get_data(filters):
	conditions = []
	values = {}
	for field in [
		"transaction_input",
		"account",
		"vendor",
		"horse_owner",
		"groom_profile",
		"horse",
		"item",
		"transaction_category",
	]:
		if filters.get(field):
			conditions.append(f"{field} = %({field})s")
			values[field] = filters.get(field)
	if filters.from_date:
		conditions.append("posting_date >= %(from_date)s")
		values["from_date"] = filters.from_date
	if filters.to_date:
		conditions.append("posting_date <= %(to_date)s")
		values["to_date"] = filters.to_date

	where = f"where {' and '.join(conditions)}" if conditions else ""
	rows = frappe.db.sql(
		f"""
		select
			name,
			posting_date,
			transaction_input,
			account,
			transaction_category,
			party_type,
			vendor,
			horse_owner,
			groom_profile,
			line_type,
			horse,
			item,
			reference_doctype,
			reference_name,
			description,
			debit,
			credit
		from `tabPayment Ledger Entry`
		{where}
		order by posting_date asc, creation asc
		""",
		values,
		as_dict=True,
	)

	balance = 0
	for row in rows:
		row.debit = flt(row.debit)
		row.credit = flt(row.credit)
		balance += row.debit - row.credit
		row.balance = balance
		row.party_display = row.vendor or row.horse_owner or row.groom_profile or row.party_type
		row.reference_display = (
			f"{row.reference_doctype}: {row.reference_name}"
			if row.reference_doctype and row.reference_name
			else row.reference_name
		)

	return rows


def get_chart(data):
	return {
		"data": {
			"labels": [row.posting_date for row in data],
			"datasets": [{"name": "Balance", "values": [row.balance for row in data]}],
		},
		"type": "line",
		"height": 240,
	}


def get_summary(data):
	debit = sum(flt(row.debit) for row in data)
	credit = sum(flt(row.credit) for row in data)
	return [
		{"value": debit, "label": "Debit", "datatype": "Currency", "indicator": "Red"},
		{"value": credit, "label": "Credit", "datatype": "Currency", "indicator": "Green"},
		{"value": debit - credit, "label": "Balance", "datatype": "Currency", "indicator": "Red" if debit >= credit else "Green"},
	]
