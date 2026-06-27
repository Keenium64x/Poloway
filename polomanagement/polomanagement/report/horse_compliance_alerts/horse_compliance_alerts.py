import frappe
from frappe.utils import add_days, getdate


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = [
		{"label": "Horse", "fieldname": "horse", "fieldtype": "Link", "options": "Horse", "width": 150},
		{"label": "Record", "fieldname": "name", "fieldtype": "Link", "options": "Horse Medical Record", "width": 150},
		{"label": "Type", "fieldname": "record_type", "fieldtype": "Data", "width": 120},
		{"label": "Summary", "fieldname": "summary", "fieldtype": "Data", "width": 260},
		{"label": "Next Due", "fieldname": "next_due_date", "fieldtype": "Date", "width": 110},
		{"label": "Days Until Due", "fieldname": "days_until_due", "fieldtype": "Int", "width": 120},
		{"label": "Status", "fieldname": "alert_status", "fieldtype": "Data", "width": 110},
		{"label": "Responsible", "fieldname": "responsible_person", "fieldtype": "Link", "options": "User", "width": 180},
	]
	return columns, get_data(filters)


def get_data(filters):
	to_date = filters.to_date or add_days(getdate(), 30)
	conditions = ["next_due_date is not null", "next_due_date <= %(to_date)s"]
	values = {"to_date": to_date}

	if filters.horse:
		conditions.append("horse = %(horse)s")
		values["horse"] = filters.horse
	if filters.record_type:
		conditions.append("record_type = %(record_type)s")
		values["record_type"] = filters.record_type
	if filters.only_open:
		conditions.append("status not in ('Completed', 'Cancelled')")

	rows = frappe.db.sql(
		f"""
		select
			name,
			horse,
			record_type,
			summary,
			next_due_date,
			status,
			responsible_person
		from `tabHorse Medical Record`
		where {" and ".join(conditions)}
		order by next_due_date asc, horse asc
		""",
		values,
		as_dict=True,
	)

	current = getdate()
	for row in rows:
		row.days_until_due = (getdate(row.next_due_date) - current).days
		if row.days_until_due < 0:
			row.alert_status = "Overdue"
		elif row.days_until_due <= 7:
			row.alert_status = "Due This Week"
		else:
			row.alert_status = "Due Soon"

	return rows

