import frappe
from frappe.utils import today


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = [
		{"label": "Match", "fieldname": "match_day", "fieldtype": "Link", "options": "Match Day", "width": 130},
		{"label": "Event", "fieldname": "event_name", "fieldtype": "Data", "width": 180},
		{"label": "Date", "fieldname": "match_date", "fieldtype": "Date", "width": 100},
		{"label": "Venue", "fieldname": "venue", "fieldtype": "Data", "width": 150},
		{"label": "Chukker", "fieldname": "chukker_number", "fieldtype": "Int", "width": 80},
		{"label": "Horse", "fieldname": "horse", "fieldtype": "Link", "options": "Horse", "width": 140},
		{"label": "Rider", "fieldname": "rider", "fieldtype": "Data", "width": 130},
		{"label": "Groom", "fieldname": "groom", "fieldtype": "Link", "options": "Groom Profile", "width": 140},
		{"label": "Status", "fieldname": "assignment_status", "fieldtype": "Data", "width": 110},
		{"label": "Tack", "fieldname": "tack_configuration", "fieldtype": "Link", "options": "Horse Tack Configuration", "width": 160},
		{"label": "Prep Instructions", "fieldname": "prep_instructions", "fieldtype": "Data", "width": 280},
	]
	return columns, get_data(filters)


def get_data(filters):
	conditions = ["match_day.status != 'Cancelled'"]
	values = {}

	if filters.match_day:
		conditions.append("match_day.name = %(match_day)s")
		values["match_day"] = filters.match_day
	elif filters.match_date:
		conditions.append("match_day.match_date = %(match_date)s")
		values["match_date"] = filters.match_date
	else:
		conditions.append("match_day.match_date = %(match_date)s")
		values["match_date"] = today()

	if filters.horse:
		conditions.append("assignment.horse = %(horse)s")
		values["horse"] = filters.horse
	if filters.assignment_status:
		conditions.append("assignment.status = %(assignment_status)s")
		values["assignment_status"] = filters.assignment_status

	return frappe.db.sql(
		f"""
		select
			match_day.name as match_day,
			match_day.event_name,
			match_day.match_date,
			match_day.venue,
			assignment.chukker_number,
			assignment.horse,
			assignment.rider,
			assignment.groom,
			assignment.status as assignment_status,
			assignment.tack_configuration,
			tack.prep_instructions
		from `tabChukker Assignment` assignment
		inner join `tabMatch Day` match_day on match_day.name = assignment.parent
		left join `tabHorse Tack Configuration` tack on tack.name = assignment.tack_configuration
		where {" and ".join(conditions)}
		order by match_day.match_date asc, assignment.chukker_number asc, assignment.idx asc
		""",
		values,
		as_dict=True,
	)

