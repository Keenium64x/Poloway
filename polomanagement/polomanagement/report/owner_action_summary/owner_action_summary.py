import frappe
from frappe.utils import add_days, flt, today


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.from_date:
		filters.from_date = today()
	if not filters.to_date:
		filters.to_date = add_days(filters.from_date, 14)
	if not filters.source:
		filters.source = "All"

	data = get_data(filters)
	return get_columns(), data, None, get_chart(data), get_summary(data)


def get_columns():
	return [
		{"label": "Source", "fieldname": "source", "fieldtype": "Data", "width": 120},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 110},
		{"label": "Type", "fieldname": "task_type", "fieldtype": "Data", "width": 130},
		{"label": "Priority", "fieldname": "priority", "fieldtype": "Data", "width": 100},
		{"label": "Count", "fieldname": "count", "fieldtype": "Int", "width": 90},
		{"label": "Issues", "fieldname": "issues", "fieldtype": "Int", "width": 90},
		{"label": "First Due", "fieldname": "first_due", "fieldtype": "Date", "width": 110},
		{"label": "Last Due", "fieldname": "last_due", "fieldtype": "Date", "width": 110},
	]


def get_data(filters):
	rows = []
	if filters.source in ("All", "Owner Task"):
		rows.extend(get_owner_tasks(filters))
	if filters.source in ("All", "Groom Task"):
		rows.extend(get_groom_tasks(filters))
	return rows


def get_owner_tasks(filters):
	conditions = ["due_date between %(from_date)s and %(to_date)s"]
	values = {"from_date": filters.from_date, "to_date": filters.to_date}
	if filters.horse:
		conditions.append("horse = %(horse)s")
		values["horse"] = filters.horse

	return frappe.db.sql(
		f"""
		select
			'Owner Task' as source,
			status,
			coalesce(task_type, 'General') as task_type,
			coalesce(priority, 'Medium') as priority,
			count(*) as count,
			0 as issues,
			min(due_date) as first_due,
			max(due_date) as last_due
		from `tabOwner Task`
		where {" and ".join(conditions)}
		group by status, coalesce(task_type, 'General'), coalesce(priority, 'Medium')
		order by first_due asc
		""",
		values,
		as_dict=True,
	)


def get_groom_tasks(filters):
	conditions = ["due_date between %(from_date)s and %(to_date)s", "owner_visible = 1"]
	values = {"from_date": filters.from_date, "to_date": filters.to_date}
	if filters.horse:
		conditions.append("horse = %(horse)s")
		values["horse"] = filters.horse

	return frappe.db.sql(
		f"""
		select
			'Groom Task' as source,
			status,
			coalesce(task_type, 'General') as task_type,
			coalesce(issue_priority, 'Normal') as priority,
			count(*) as count,
			sum(case when issue_reported = 1 and coalesce(issue_status, 'Open') != 'Resolved' then 1 else 0 end) as issues,
			min(due_date) as first_due,
			max(due_date) as last_due
		from `tabTask`
		where {" and ".join(conditions)}
		group by status, coalesce(task_type, 'General'), coalesce(issue_priority, 'Normal')
		order by first_due asc
		""",
		values,
		as_dict=True,
	)


def get_chart(data):
	statuses = ["Open", "Completed", "Cancelled"]
	return {
		"data": {
			"labels": statuses,
			"datasets": [{"name": "Tasks", "values": [sum(flt(row.count) for row in data if row.status == status) for status in statuses]}],
		},
		"type": "bar",
		"height": 260,
	}


def get_summary(data):
	open_tasks = sum(flt(row.count) for row in data if row.status == "Open")
	completed = sum(flt(row.count) for row in data if row.status == "Completed")
	issues = sum(flt(row.issues) for row in data)
	return [
		{"value": open_tasks, "label": "Open Actions", "datatype": "Int", "indicator": "Orange"},
		{"value": completed, "label": "Completed", "datatype": "Int", "indicator": "Green"},
		{"value": issues, "label": "Open Issues", "datatype": "Int", "indicator": "Red" if issues else "Green"},
	]
