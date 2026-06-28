import frappe
from frappe.utils import add_months, flt, today


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.from_date:
		filters.from_date = add_months(today(), -3)
	if not filters.to_date:
		filters.to_date = today()

	data = get_data(filters)
	add_scores(data)
	return get_columns(), data, None, get_chart(data), get_summary(data)


def get_columns():
	return [
		{"label": "Horse", "fieldname": "horse", "fieldtype": "Link", "options": "Horse", "width": 130},
		{"label": "Horse Name", "fieldname": "horse_name", "fieldtype": "Data", "width": 160},
		{"label": "Availability", "fieldname": "availability_status", "fieldtype": "Data", "width": 120},
		{"label": "Playing Status", "fieldname": "playing_status", "fieldtype": "Data", "width": 120},
		{"label": "Training Sessions", "fieldname": "training_sessions", "fieldtype": "Int", "width": 130},
		{"label": "Completed Training", "fieldname": "completed_training", "fieldtype": "Int", "width": 130},
		{"label": "Needs Follow Up", "fieldname": "follow_up_training", "fieldtype": "Int", "width": 120},
		{"label": "Match Chukkers", "fieldname": "match_chukkers", "fieldtype": "Int", "width": 120},
		{"label": "Open Issues", "fieldname": "open_issues", "fieldtype": "Int", "width": 100},
		{"label": "Medical Due", "fieldname": "medical_due", "fieldtype": "Int", "width": 100},
		{"label": "Expenses", "fieldname": "expenses", "fieldtype": "Currency", "width": 120},
		{"label": "Readiness Score", "fieldname": "readiness_score", "fieldtype": "Float", "width": 120},
	]


def get_data(filters):
	conditions = []
	values = {"from_date": filters.from_date, "to_date": filters.to_date}
	if filters.horse:
		conditions.append("horse.name = %(horse)s")
		values["horse"] = filters.horse
	if filters.availability_status:
		conditions.append("horse.availability_status = %(availability_status)s")
		values["availability_status"] = filters.availability_status

	where_clause = f"where {' and '.join(conditions)}" if conditions else ""
	return frappe.db.sql(
		f"""
		select
			horse.name as horse,
			horse.name1 as horse_name,
			horse.availability_status,
			horse.playing_status,
			coalesce(training.training_sessions, 0) as training_sessions,
			coalesce(training.completed_training, 0) as completed_training,
			coalesce(training.follow_up_training, 0) as follow_up_training,
			coalesce(matches.match_chukkers, 0) as match_chukkers,
			coalesce(tasks.open_issues, 0) as open_issues,
			coalesce(medical.medical_due, 0) as medical_due,
			coalesce(expenses.expenses, 0) as expenses
		from `tabHorse` horse
		left join (
			select
				horse,
				count(*) as training_sessions,
				sum(case when outcome = 'Completed' then 1 else 0 end) as completed_training,
				sum(case when outcome = 'Needs Follow Up' then 1 else 0 end) as follow_up_training
			from `tabHorse Training Record`
			where training_date between %(from_date)s and %(to_date)s
			group by horse
		) training on training.horse = horse.name
		left join (
			select assignment.horse, count(*) as match_chukkers
			from `tabChukker Assignment` assignment
			inner join `tabMatch Day` match_day on match_day.name = assignment.parent
			where match_day.match_date between %(from_date)s and %(to_date)s
				and match_day.status != 'Cancelled'
			group by assignment.horse
		) matches on matches.horse = horse.name
		left join (
			select horse, count(*) as open_issues
			from `tabTask`
			where owner_visible = 1
				and issue_reported = 1
				and coalesce(issue_status, 'Open') != 'Resolved'
			group by horse
		) tasks on tasks.horse = horse.name
		left join (
			select horse, count(*) as medical_due
			from `tabHorse Medical Record`
			where next_due_date is not null
				and next_due_date <= %(to_date)s
				and coalesce(status, 'Open') != 'Completed'
			group by horse
		) medical on medical.horse = horse.name
		left join (
			select line.horse, sum(line.total) as expenses
			from `tabTransaction Input Line` line
			inner join `tabTransaction Input` tx on tx.name = line.parent
			where tx.docstatus = 1
				and tx.direction = 'Money Out'
				and tx.transaction_date between %(from_date)s and %(to_date)s
			group by line.horse
		) expenses on expenses.horse = horse.name
		{where_clause}
		order by horse.name1 asc
		""",
		values,
		as_dict=True,
	)


def add_scores(data):
	for row in data:
		row.readiness_score = (
			flt(row.completed_training) * 2
			+ flt(row.match_chukkers)
			- flt(row.follow_up_training) * 2
			- flt(row.open_issues) * 3
			- flt(row.medical_due) * 3
		)


def get_chart(data):
	top_rows = sorted(data, key=lambda row: flt(row.readiness_score), reverse=True)[:10]
	return {
		"data": {
			"labels": [row.horse_name or row.horse for row in top_rows],
			"datasets": [{"name": "Readiness Score", "values": [flt(row.readiness_score) for row in top_rows]}],
		},
		"type": "bar",
		"height": 280,
		"colors": ["#C9A227"],
	}


def get_summary(data):
	available = sum(1 for row in data if row.availability_status == "Available")
	open_issues = sum(flt(row.open_issues) for row in data)
	medical_due = sum(flt(row.medical_due) for row in data)
	return [
		{"value": available, "label": "Available Horses", "datatype": "Int", "indicator": "Green"},
		{"value": open_issues, "label": "Open Issues", "datatype": "Int", "indicator": "Red" if open_issues else "Green"},
		{"value": medical_due, "label": "Medical Due", "datatype": "Int", "indicator": "Orange" if medical_due else "Green"},
	]
