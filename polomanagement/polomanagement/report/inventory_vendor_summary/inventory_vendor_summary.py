import frappe
from frappe.utils import flt


GROUPS = {
	"Category": "coalesce(category.item_category_name, item.item_category, 'No Category')",
	"Location": "coalesce(location.location_name, item.inventory_location, 'No Location')",
	"Responsible Role": "coalesce(item.responsible_role, 'Unassigned')",
}


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.group_by:
		filters.group_by = "Category"
	data = get_data(filters)
	return get_columns(filters), data, None, get_chart(data, filters), get_summary(data)


def get_columns(filters):
	return [
		{"label": filters.group_by, "fieldname": "group_name", "fieldtype": "Data", "width": 220},
		{"label": "Items", "fieldname": "items", "fieldtype": "Int", "width": 90},
		{"label": "Stock Qty", "fieldname": "stock_qty", "fieldtype": "Float", "width": 110},
		{"label": "Stock Value", "fieldname": "stock_value", "fieldtype": "Currency", "width": 130},
		{"label": "Average Rate", "fieldname": "average_rate", "fieldtype": "Currency", "width": 120},
		{"label": "Open Quotes", "fieldname": "open_quotes", "fieldtype": "Int", "width": 110},
		{"label": "Selected Quotes", "fieldname": "selected_quotes", "fieldtype": "Int", "width": 120},
	]


def get_data(filters):
	group_expr = GROUPS.get(filters.group_by, GROUPS["Category"])
	conditions = []
	values = {}
	if filters.active_only:
		conditions.append("item.is_active = 1")
	if filters.item_category:
		conditions.append("item.item_category = %(item_category)s")
		values["item_category"] = filters.item_category
	if filters.inventory_location:
		conditions.append("item.inventory_location = %(inventory_location)s")
		values["inventory_location"] = filters.inventory_location

	where_clause = f"where {' and '.join(conditions)}" if conditions else ""
	return frappe.db.sql(
		f"""
		select
			{group_expr} as group_name,
			count(distinct item.name) as items,
			sum(item.quantity_on_hand) as stock_qty,
			sum(item.total_value) as stock_value,
			avg(nullif(item.valuation_rate, 0)) as average_rate,
			count(distinct case when quote.status in ('Draft', 'Submitted') then quote.name end) as open_quotes,
			count(distinct case when quote.status = 'Selected' then quote.name end) as selected_quotes
		from `tabItem` item
		left join `tabItem Category` category on category.name = item.item_category
		left join `tabInventory Location` location on location.name = item.inventory_location
		left join `tabVendor Quote Line` quote_line on quote_line.item = item.name
		left join `tabVendor Quote` quote on quote.name = quote_line.parent
		{where_clause}
		group by {group_expr}
		order by stock_value desc, items desc
		""",
		values,
		as_dict=True,
	)


def get_chart(data, filters):
	top_rows = data[:10]
	return {
		"data": {
			"labels": [row.group_name for row in top_rows],
			"datasets": [{"name": "Stock Value", "values": [flt(row.stock_value) for row in top_rows]}],
		},
		"type": "bar",
		"height": 280,
		"colors": ["#2F9E44"],
	}


def get_summary(data):
	items = sum(flt(row.get("items")) for row in data)
	value = sum(flt(row.stock_value) for row in data)
	open_quotes = sum(flt(row.open_quotes) for row in data)
	return [
		{"value": items, "label": "Items", "datatype": "Int", "indicator": "Blue"},
		{"value": value, "label": "Stock Value", "datatype": "Currency", "indicator": "Green"},
		{"value": open_quotes, "label": "Open Quotes", "datatype": "Int", "indicator": "Orange" if open_quotes else "Green"},
	]
