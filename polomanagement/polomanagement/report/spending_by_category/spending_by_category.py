import frappe
from frappe.utils import add_months, flt, get_first_day, today


GROUPS = {
	"Category": "coalesce(line.cost_category, tx.transaction_category, 'Other')",
	"Vendor": "coalesce(vendor.vendor_name, tx.vendor, 'No Vendor')",
	"Horse": "coalesce(horse.name1, line.horse, 'No Horse')",
	"Item": "coalesce(item.item_name, line.item, 'No Item')",
	"Line Type": "coalesce(line.line_type, 'Other')",
}


def execute(filters=None):
	filters = frappe._dict(filters or {})
	set_default_dates(filters)
	data = get_data(filters)
	return get_columns(filters), data, None, get_chart(data, filters), get_summary(data, filters)


def set_default_dates(filters):
	if not filters.to_date:
		filters.to_date = today()
	if not filters.from_date:
		filters.from_date = get_first_day(add_months(filters.to_date, -6))
	if not filters.direction:
		filters.direction = "Money Out"
	if not filters.group_by:
		filters.group_by = "Category"


def get_columns(filters):
	return [
		{"label": filters.group_by, "fieldname": "group_name", "fieldtype": "Data", "width": 220},
		{"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 130},
		{"label": "Transactions", "fieldname": "transactions", "fieldtype": "Int", "width": 110},
		{"label": "First Date", "fieldname": "first_date", "fieldtype": "Date", "width": 110},
		{"label": "Last Date", "fieldname": "last_date", "fieldtype": "Date", "width": 110},
	]


def get_data(filters):
	group_expr = GROUPS.get(filters.group_by, GROUPS["Category"])
	conditions = ["tx.docstatus = 1", "tx.transaction_date between %(from_date)s and %(to_date)s"]
	values = {"from_date": filters.from_date, "to_date": filters.to_date}

	if filters.direction and filters.direction != "Both":
		conditions.append("tx.direction = %(direction)s")
		values["direction"] = filters.direction
	if filters.horse:
		conditions.append("line.horse = %(horse)s")
		values["horse"] = filters.horse
	if filters.vendor:
		conditions.append("tx.vendor = %(vendor)s")
		values["vendor"] = filters.vendor

	return frappe.db.sql(
		f"""
		select
			{group_expr} as group_name,
			sum(line.total) as amount,
			count(distinct tx.name) as transactions,
			min(tx.transaction_date) as first_date,
			max(tx.transaction_date) as last_date
		from `tabTransaction Input` tx
		inner join `tabTransaction Input Line` line on line.parent = tx.name
		left join `tabVendor` vendor on vendor.name = tx.vendor
		left join `tabHorse` horse on horse.name = line.horse
		left join `tabItem` item on item.name = line.item
		where {" and ".join(conditions)}
		group by {group_expr}
		order by amount desc
		""",
		values,
		as_dict=True,
	)


def get_chart(data, filters):
	top_rows = data[:10]
	direction = filters.direction or "Amount"
	color = "#64748B"
	if direction == "Money Out":
		color = "#C92A2A"
	elif direction == "Money In":
		color = "#2F9E44"

	return {
		"data": {
			"labels": [row.group_name for row in top_rows],
			"datasets": [{"name": direction if direction != "Both" else "Amount", "values": [flt(row.amount) for row in top_rows]}],
		},
		"type": "bar",
		"height": 280,
		"colors": [color],
	}


def get_summary(data, filters):
	total = sum(flt(row.amount) for row in data)
	return [
		{"value": total, "label": filters.direction if filters.direction != "Both" else "Total", "datatype": "Currency", "indicator": "Red" if filters.direction == "Money Out" else "Green"},
		{"value": len(data), "label": "Groups", "datatype": "Int", "indicator": "Blue"},
	]
