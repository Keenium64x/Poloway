import frappe
from frappe.utils import add_days, date_diff, flt, today


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.from_date:
		filters.from_date = today()
	if not filters.to_date:
		filters.to_date = add_days(filters.from_date, 90)

	data = get_data(filters)
	return get_columns(), data, None, get_chart(data), get_summary(data)


def get_columns():
	return [
		{"label": "Match", "fieldname": "match_day", "fieldtype": "Link", "options": "Match Day", "width": 130},
		{"label": "Event", "fieldname": "event_name", "fieldtype": "Data", "width": 190},
		{"label": "Date", "fieldname": "match_date", "fieldtype": "Date", "width": 110},
		{"label": "Days Until", "fieldname": "days_until", "fieldtype": "Int", "width": 95},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 110},
		{"label": "Venue", "fieldname": "venue", "fieldtype": "Data", "width": 160},
		{"label": "Team", "fieldname": "team", "fieldtype": "Data", "width": 140},
		{"label": "Opponent", "fieldname": "opponent", "fieldtype": "Data", "width": 140},
		{"label": "Chukkers", "fieldname": "chukkers", "fieldtype": "Int", "width": 90},
		{"label": "Horses Used", "fieldname": "horses_used", "fieldtype": "Int", "width": 110},
		{"label": "Grooms", "fieldname": "grooms", "fieldtype": "Int", "width": 90},
		{"label": "Match Count", "fieldname": "match_count", "fieldtype": "Int", "width": 95},
	]


def get_data(filters):
	conditions = ["match_day.match_date between %(from_date)s and %(to_date)s"]
	values = {"from_date": filters.from_date, "to_date": filters.to_date}
	if filters.status:
		conditions.append("match_day.status = %(status)s")
		values["status"] = filters.status
	else:
		conditions.append("match_day.status != 'Cancelled'")

	rows = frappe.db.sql(
		f"""
		select
			match_day.name as match_day,
			match_day.event_name,
			match_day.match_date,
			match_day.status,
			match_day.venue,
			match_day.team,
			match_day.opponent,
			count(assignment.name) as chukkers,
			count(distinct assignment.horse) as horses_used,
			count(distinct assignment.groom) as grooms,
			1 as match_count
		from `tabMatch Day` match_day
		left join `tabChukker Assignment` assignment on assignment.parent = match_day.name
		where {" and ".join(conditions)}
		group by match_day.name
		order by match_day.match_date asc, match_day.creation asc
		""",
		values,
		as_dict=True,
	)

	for row in rows:
		row.days_until = date_diff(row.match_date, today()) if row.match_date else None
	return rows


def get_chart(data):
	labels = [row.event_name or row.match_day for row in data[:8]]
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": "Chukkers", "values": [flt(row.chukkers) for row in data[:8]]},
				{"name": "Horses Used", "values": [flt(row.horses_used) for row in data[:8]]},
			],
		},
		"type": "bar",
		"height": 260,
		"colors": ["#C9A227", "#64748B"],
	}


def get_summary(data):
	next_match = data[0] if data else None
	chukkers = sum(flt(row.chukkers) for row in data)
	return [
		{"value": len(data), "label": "Upcoming Matches", "datatype": "Int", "indicator": "Blue"},
		{
			"value": next_match.days_until if next_match else 0,
			"label": "Days To Next Match",
			"datatype": "Int",
			"indicator": "Orange" if next_match else "Gray",
		},
		{"value": chukkers, "label": "Planned Chukkers", "datatype": "Int", "indicator": "Green"},
	]
