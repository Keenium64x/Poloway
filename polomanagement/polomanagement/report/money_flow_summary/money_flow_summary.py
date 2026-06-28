import frappe
from frappe.utils import add_months, flt, get_first_day, today


def execute(filters=None):
	filters = frappe._dict(filters or {})
	set_default_dates(filters)
	columns = get_columns()
	data = get_data(filters)
	return columns, data, None, get_chart(data), get_summary(data)


def set_default_dates(filters):
	if not filters.to_date:
		filters.to_date = today()
	if not filters.from_date:
		filters.from_date = get_first_day(add_months(filters.to_date, -12))
	if not filters.period:
		filters.period = "Monthly"


def get_columns():
	return [
		{"label": "Period", "fieldname": "period", "fieldtype": "Data", "width": 110},
		{"label": "Category", "fieldname": "category", "fieldtype": "Data", "width": 160},
		{"label": "Income", "fieldname": "income", "fieldtype": "Currency", "width": 130},
		{"label": "Outflow", "fieldname": "outflow", "fieldtype": "Currency", "width": 130},
		{"label": "Net", "fieldname": "net", "fieldtype": "Currency", "width": 130},
		{"label": "Transactions", "fieldname": "transactions", "fieldtype": "Int", "width": 110},
	]


def get_period_expression(period):
	if period == "Daily":
		return "date_format(tx.transaction_date, '%%Y-%%m-%%d')"
	if period == "Weekly":
		return "concat(year(tx.transaction_date), '-W', lpad(week(tx.transaction_date, 3), 2, '0'))"
	return "date_format(tx.transaction_date, '%%Y-%%m')"


def get_data(filters):
	period_expr = get_period_expression(filters.period)
	conditions = ["tx.docstatus = 1", "tx.transaction_date between %(from_date)s and %(to_date)s"]
	values = {"from_date": filters.from_date, "to_date": filters.to_date}

	if filters.transaction_category:
		conditions.append("coalesce(line.cost_category, tx.transaction_category, 'Other') = %(category)s")
		values["category"] = filters.transaction_category
	if filters.horse:
		conditions.append("line.horse = %(horse)s")
		values["horse"] = filters.horse
	if filters.vendor:
		conditions.append("tx.vendor = %(vendor)s")
		values["vendor"] = filters.vendor

	rows = frappe.db.sql(
		f"""
		select
			{period_expr} as period,
			coalesce(line.cost_category, tx.transaction_category, 'Other') as category,
			sum(case when tx.direction = 'Money In' then line.total else 0 end) as income,
			sum(case when tx.direction = 'Money Out' then line.total else 0 end) as outflow,
			count(distinct tx.name) as transactions
		from `tabTransaction Input` tx
		inner join `tabTransaction Input Line` line on line.parent = tx.name
		where {" and ".join(conditions)}
		group by {period_expr}, coalesce(line.cost_category, tx.transaction_category, 'Other')
		order by period asc, outflow desc, income desc
		""",
		values,
		as_dict=True,
	)

	for row in rows:
		row.income = flt(row.income)
		row.outflow = flt(row.outflow)
		row.net = row.income - row.outflow
	return rows


def get_chart(data):
	periods = sorted({row.period for row in data})
	return {
		"data": {
			"labels": periods,
			"datasets": [
				{"name": "Income", "values": [sum(flt(row.income) for row in data if row.period == period) for period in periods]},
				{"name": "Outflow", "values": [sum(flt(row.outflow) for row in data if row.period == period) for period in periods]},
			],
		},
		"type": "bar",
		"height": 280,
		"colors": ["#2F9E44", "#C92A2A"],
	}


def get_summary(data):
	income = sum(flt(row.income) for row in data)
	outflow = sum(flt(row.outflow) for row in data)
	net = income - outflow
	return [
		{"value": income, "label": "Income", "datatype": "Currency", "indicator": "Green"},
		{"value": outflow, "label": "Outflow", "datatype": "Currency", "indicator": "Red"},
		{"value": net, "label": "Net Cash Flow", "datatype": "Currency", "indicator": "Green" if net >= 0 else "Red"},
	]
