import frappe


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = [
		{"label": "Task", "fieldname": "name", "fieldtype": "Link", "options": "Task", "width": 150},
		{"label": "Date", "fieldname": "due_date", "fieldtype": "Date", "width": 110},
		{"label": "Horse", "fieldname": "horse", "fieldtype": "Link", "options": "Horse", "width": 150},
		{"label": "Subject", "fieldname": "subject", "fieldtype": "Data", "width": 220},
		{"label": "Type", "fieldname": "task_type", "fieldtype": "Data", "width": 100},
		{"label": "Priority", "fieldname": "issue_priority", "fieldtype": "Data", "width": 100},
		{"label": "Issue Status", "fieldname": "issue_status", "fieldtype": "Data", "width": 130},
		{"label": "Completed By", "fieldname": "completed_by", "fieldtype": "Link", "options": "User", "width": 180},
		{"label": "Completion Notes", "fieldname": "completion_notes", "fieldtype": "Data", "width": 320},
		{"label": "Owner Follow Up", "fieldname": "owner_follow_up", "fieldtype": "Data", "width": 320},
	]
	return columns, get_data(filters)


def get_data(filters):
	conditions = {"issue_reported": 1, "owner_visible": 1}
	if filters.issue_status:
		conditions["issue_status"] = filters.issue_status
	if filters.issue_priority:
		conditions["issue_priority"] = filters.issue_priority
	if filters.horse:
		conditions["horse"] = filters.horse
	if filters.from_date and filters.to_date:
		conditions["due_date"] = ["between", [filters.from_date, filters.to_date]]
	elif filters.from_date:
		conditions["due_date"] = [">=", filters.from_date]
	elif filters.to_date:
		conditions["due_date"] = ["<=", filters.to_date]

	rows = frappe.get_all(
		"Task",
		filters=conditions,
		fields=[
			"name",
			"due_date",
			"horse",
			"subject",
			"task_type",
			"issue_priority",
			"issue_status",
			"completed_by",
			"completion_notes",
			"owner_follow_up",
		],
		order_by="due_date desc, modified desc",
	)
	return sorted(rows, key=issue_sort_key)


def issue_sort_key(row):
	status_order = {"Open": 0, "Acknowledged": 1, "Resolved": 2}
	priority_order = {"Urgent": 0, "High": 1, "Normal": 2, "Low": 3}
	return (
		status_order.get(row.get("issue_status"), 9),
		priority_order.get(row.get("issue_priority"), 9),
		row.get("due_date") or "",
	)
