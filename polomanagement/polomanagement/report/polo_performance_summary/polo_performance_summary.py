import frappe
from frappe.utils import add_months, flt, today


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.from_date:
		filters.from_date = add_months(today(), -3)
	if not filters.to_date:
		filters.to_date = add_months(today(), 3)

	data = get_data(filters)
	return get_columns(), data, None, get_chart(data), get_summary(data)


def get_columns():
	return [
		{"label": "Match", "fieldname": "match_day", "fieldtype": "Link", "options": "Match Day", "width": 130},
		{"label": "Event", "fieldname": "event_name", "fieldtype": "Data", "width": 190},
		{"label": "Date", "fieldname": "match_date", "fieldtype": "Date", "width": 110},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 110},
		{"label": "Venue", "fieldname": "venue", "fieldtype": "Data", "width": 160},
		{"label": "Opponent", "fieldname": "opponent", "fieldtype": "Data", "width": 140},
		{"label": "Chukkers", "fieldname": "chukkers", "fieldtype": "Int", "width": 90},
		{"label": "Horses Used", "fieldname": "horses_used", "fieldtype": "Int", "width": 110},
		{"label": "Grooms", "fieldname": "grooms", "fieldtype": "Int", "width": 90},
	]


def get_data(filters):
	conditions = ["match_day.match_date between %(from_date)s and %(to_date)s"]
	values = {"from_date": filters.from_date, "to_date": filters.to_date}
	if filters.status:
		conditions.append("match_day.status = %(status)s")
		values["status"] = filters.status

	return frappe.db.sql(
		f"""
		select
			match_day.name as match_day,
			match_day.event_name,
			match_day.match_date,
			match_day.status,
			match_day.venue,
			match_day.opponent,
			count(assignment.name) as chukkers,
			count(distinct assignment.horse) as horses_used,
			count(distinct assignment.groom) as grooms
		from `tabMatch Day` match_day
		left join `tabChukker Assignment` assignment on assignment.parent = match_day.name
		where {" and ".join(conditions)}
		group by match_day.name
		order by match_day.match_date asc, match_day.creation asc
		""",
		values,
		as_dict=True,
	)


def get_chart(data):
	statuses = ["Planned", "In Progress", "Completed", "Cancelled"]
	return {
		"data": {
			"labels": statuses,
			"datasets": [{"name": "Matches", "values": [sum(1 for row in data if row.status == status) for status in statuses]}],
		},
		"type": "donut",
		"height": 260,
	}


def get_summary(data):
	upcoming = sum(1 for row in data if row.match_date and str(row.match_date) >= today() and row.status != "Cancelled")
	completed = sum(1 for row in data if row.status == "Completed")
	chukkers = sum(flt(row.chukkers) for row in data)
	return [
		{"value": upcoming, "label": "Upcoming", "datatype": "Int", "indicator": "Blue"},
		{"value": completed, "label": "Completed", "datatype": "Int", "indicator": "Green"},
		{"value": chukkers, "label": "Chukkers Planned", "datatype": "Int", "indicator": "Orange"},
	]
