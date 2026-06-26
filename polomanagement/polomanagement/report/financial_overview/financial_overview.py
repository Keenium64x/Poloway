import frappe
from frappe.utils import flt


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	report_summary = get_summary(data)
	return columns, data, None, chart, report_summary


def get_columns():
	return [
		{"label": "Category", "fieldname": "transaction_category", "fieldtype": "Data", "width": 160},
		{"label": "Money Out", "fieldname": "money_out", "fieldtype": "Currency", "width": 130},
		{"label": "Money In", "fieldname": "money_in", "fieldtype": "Currency", "width": 130},
		{"label": "Net", "fieldname": "net", "fieldtype": "Currency", "width": 130},
		{"label": "Records", "fieldname": "records", "fieldtype": "Int", "width": 90},
		{"label": "Last Payment", "fieldname": "last_payment", "fieldtype": "Link", "options": "Payment Record", "width": 140},
		{"label": "Last Date", "fieldname": "last_date", "fieldtype": "Date", "width": 110},
	]


def get_data(filters):
	conditions = ["payment.docstatus = 1"]
	values = {}

	if filters.from_date:
		conditions.append("payment.posting_date >= %(from_date)s")
		values["from_date"] = filters.from_date
	if filters.to_date:
		conditions.append("payment.posting_date <= %(to_date)s")
		values["to_date"] = filters.to_date
	if filters.vendor:
		conditions.append("payment.vendor = %(vendor)s")
		values["vendor"] = filters.vendor
	if filters.transaction_category:
		conditions.append("coalesce(line.cost_category, payment.transaction_category, 'Other') = %(category)s")
		values["category"] = filters.transaction_category
	if filters.horse:
		conditions.append("line.horse = %(horse)s")
		values["horse"] = filters.horse

	rows = frappe.db.sql(
		f"""
		select
			coalesce(line.cost_category, payment.transaction_category, 'Other') as transaction_category,
			sum(case when payment.direction = 'Money Out' then line.total else 0 end) as money_out,
			sum(case when payment.direction = 'Money In' then line.total else 0 end) as money_in,
			count(distinct payment.name) as records,
			max(payment.posting_date) as last_date
		from `tabPayment Record Line` line
		inner join `tabPayment Record` payment on payment.name = line.parent
		where {" and ".join(conditions)}
		group by coalesce(line.cost_category, payment.transaction_category, 'Other')
		order by money_out desc, money_in desc
		""",
		values,
		as_dict=True,
	)

	for row in rows:
		row.money_out = flt(row.money_out)
		row.money_in = flt(row.money_in)
		row.net = row.money_in - row.money_out
		row.last_payment = get_last_payment(row.transaction_category, filters)

	return rows


def get_last_payment(category, filters):
	conditions = [
		"payment.docstatus = 1",
		"coalesce(line.cost_category, payment.transaction_category, 'Other') = %(category)s",
	]
	values = {"category": category}

	if filters.from_date:
		conditions.append("payment.posting_date >= %(from_date)s")
		values["from_date"] = filters.from_date
	if filters.to_date:
		conditions.append("payment.posting_date <= %(to_date)s")
		values["to_date"] = filters.to_date
	if filters.vendor:
		conditions.append("payment.vendor = %(vendor)s")
		values["vendor"] = filters.vendor
	if filters.horse:
		conditions.append("line.horse = %(horse)s")
		values["horse"] = filters.horse

	result = frappe.db.sql(
		f"""
		select payment.name
		from `tabPayment Record Line` line
		inner join `tabPayment Record` payment on payment.name = line.parent
		where {" and ".join(conditions)}
		order by payment.posting_date desc, payment.creation desc
		limit 1
		""",
		values,
	)
	return result[0][0] if result else None


def get_chart(data):
	return {
		"data": {
			"labels": [row.transaction_category for row in data],
			"datasets": [
				{"name": "Money Out", "values": [row.money_out for row in data]},
				{"name": "Money In", "values": [row.money_in for row in data]},
			],
		},
		"type": "bar",
		"height": 280,
	}


def get_summary(data):
	income = sum(flt(row.money_in) for row in data)
	expenses = sum(flt(row.money_out) for row in data)
	net = income - expenses
	return [
		{"value": expenses, "label": "Expenses", "datatype": "Currency", "indicator": "Red"},
		{"value": income, "label": "Income", "datatype": "Currency", "indicator": "Green"},
		{"value": net, "label": "Net", "datatype": "Currency", "indicator": "Green" if net >= 0 else "Red"},
	]
