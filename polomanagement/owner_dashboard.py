import frappe
from frappe.utils import add_days, flt, getdate, today


def today_bounds():
	current = today()
	return f"{current} 00:00:00", f"{current} 23:59:59"


def duration_filters():
	day_start, day_end = today_bounds()
	return {
		"starts_on": ["<=", day_end],
		"ends_on": [">=", day_start],
	}


def count_tasks(extra_filters=None):
	filters = {"owner_visible": 1}
	filters.update(extra_filters or {})
	return frappe.db.count("Task", filters)


@frappe.whitelist()
def open_issues(filters=None):
	return {
		"value": count_tasks({"issue_reported": 1, "issue_status": ["in", ["Open", "Acknowledged"]]}),
		"fieldtype": "Int",
		"route": ["query-report", "Owner Task Issues"],
		"route_options": {"issue_status": "Open"},
	}


@frappe.whitelist()
def today_open_tasks(filters=None):
	task_filters = {"status": "Open"}
	task_filters.update(duration_filters())
	return {
		"value": count_tasks(task_filters),
		"fieldtype": "Int",
		"route": ["task", "view", "kanban", "Whiteboard"],
	}


@frappe.whitelist()
def today_completed_tasks(filters=None):
	task_filters = {"status": "Completed"}
	task_filters.update(duration_filters())
	return {
		"value": count_tasks(task_filters),
		"fieldtype": "Int",
		"route": ["List", "Task", "List"],
		"route_options": {"status": "Completed", "due_date": today()},
	}


@frappe.whitelist()
def owner_upcoming_tasks(filters=None):
	return {
		"value": frappe.db.count(
			"Owner Task",
			{
				"status": "Open",
				"due_date": ["between", [today(), add_days(today(), 14)]],
			},
		),
		"fieldtype": "Int",
		"route": ["List", "Owner Task", "Calendar"],
	}


@frappe.whitelist()
def horses_needing_attention(filters=None):
	horse_names = set(
		frappe.get_all(
			"Horse",
			filters={"availability_status": ["in", ["Unavailable", "Reserved"]]},
			pluck="name",
		)
	)
	horse_names.update(
		frappe.get_all(
			"Horse",
			filters={"playing_status": ["in", ["Injured", "Resting"]]},
			pluck="name",
		)
	)
	return {
		"value": len(horse_names),
		"fieldtype": "Int",
		"route": ["List", "Horse", "List"],
	}


@frappe.whitelist()
def get_horse_dashboard(horse):
	doc = frappe.get_doc("Horse", horse)
	doc.check_permission("read")

	return {
		"summary": get_horse_summary(doc),
		"metrics": get_horse_metrics(horse),
		"issues": get_recent_issues(horse),
		"records": get_recent_records(horse),
		"upcoming": get_upcoming_items(horse),
		"money": get_horse_money(horse),
	}


def get_horse_summary(doc):
	return {
		"name": doc.name,
		"display_name": doc.name1,
		"sex": doc.sex,
		"breed": doc.breed,
		"colour": doc.colour,
		"playing_status": doc.playing_status,
		"availability_status": doc.availability_status,
		"current_location": doc.current_location,
		"stable_number": doc.stable_number,
		"height": doc.height,
		"weight": doc.weight,
		"passport": doc.passport,
		"special_instructions": doc.special_instructions,
	}


def get_horse_metrics(horse):
	return {
		"open_tasks": frappe.db.count("Task", {"horse": horse, "owner_visible": 1, "status": "Open"}),
		"open_issues": frappe.db.count(
			"Task",
			{"horse": horse, "owner_visible": 1, "issue_reported": 1, "issue_status": ["!=", "Resolved"]},
		),
		"medical_30d": count_since("Horse Medical Record", "record_date", horse, 30),
		"training_30d": count_since("Horse Training Record", "training_date", horse, 30),
	}


def get_horse_money(horse):
	return {
		"metrics": {
			"expenses_30d": sum_horse_payments(horse, add_days(getdate(), -30), direction="Money Out"),
			"expenses_ytd": sum_horse_payments(horse, f"{getdate().year}-01-01", direction="Money Out"),
			"income_ytd": sum_horse_payments(horse, f"{getdate().year}-01-01", direction="Money In"),
			"unposted": count_unposted_transactions(horse),
		},
		"payments": get_recent_horse_payments(horse),
		"quotes": get_horse_quotes(horse),
		"unposted": get_unposted_transactions(horse),
	}


def sum_horse_payments(horse, from_date=None, direction=None):
	conditions = ["payment.docstatus = 1", "line.horse = %(horse)s"]
	values = {"horse": horse}
	if from_date:
		conditions.append("payment.posting_date >= %(from_date)s")
		values["from_date"] = from_date
	if direction:
		conditions.append("payment.direction = %(direction)s")
		values["direction"] = direction

	result = frappe.db.sql(
		f"""
		select sum(line.total)
		from `tabPayment Record Line` line
		inner join `tabPayment Record` payment on payment.name = line.parent
		where {" and ".join(conditions)}
		""",
		values,
	)
	return flt(result[0][0] if result else 0)


def count_unposted_transactions(horse):
	return len(get_unposted_transaction_names(horse))


def get_unposted_transaction_names(horse):
	return frappe.db.sql_list(
		"""
		select distinct tx.name
		from `tabTransaction Input` tx
		inner join `tabTransaction Input Line` line on line.parent = tx.name
		where ifnull(tx.payment_record, '') = ''
			and tx.status != 'Cancelled'
			and line.horse = %(horse)s
		""",
		{"horse": horse},
	)


def get_recent_horse_payments(horse):
	return frappe.db.sql(
		"""
		select
			payment.name,
			payment.posting_date,
			payment.direction,
			payment.transaction_category,
			payment.vendor,
			line.description,
			line.total
		from `tabPayment Record Line` line
		inner join `tabPayment Record` payment on payment.name = line.parent
		where payment.docstatus = 1
			and line.horse = %(horse)s
		order by payment.posting_date desc, payment.creation desc, line.idx asc
		limit 5
		""",
		{"horse": horse},
		as_dict=True,
	)


def get_horse_quotes(horse):
	rows = frappe.get_all(
		"Vendor Quote",
		filters={"linked_horse": horse, "status": ["in", ["Draft", "Submitted", "Selected"]]},
		fields=["name", "quote_title", "vendor", "status", "quote_date", "valid_until", "total_amount"],
		order_by="quote_date desc, total_amount asc",
		limit=5,
	)
	status_order = {"Selected": 0, "Submitted": 1, "Draft": 2}
	return sorted(rows, key=lambda row: (status_order.get(row.status, 9), flt(row.total_amount)))


def get_unposted_transactions(horse):
	names = get_unposted_transaction_names(horse)
	if not names:
		return []

	return frappe.get_all(
		"Transaction Input",
		filters={"name": ["in", names]},
		fields=["name", "transaction_date", "transaction_type", "transaction_category", "vendor", "total_amount"],
		order_by="transaction_date desc, creation desc",
		limit=5,
	)


def count_since(doctype, date_field, horse, days):
	return frappe.db.count(
		doctype,
		{
			"horse": horse,
			date_field: [">=", add_days(getdate(), -days)],
		},
	)


def get_recent_issues(horse):
	rows = frappe.get_all(
		"Task",
		filters={"horse": horse, "owner_visible": 1, "issue_reported": 1},
		fields=[
			"name",
			"subject",
			"due_date",
			"issue_priority",
			"issue_status",
			"completion_notes",
			"owner_follow_up",
		],
		order_by="modified desc",
		limit=5,
	)
	return sorted(rows, key=lambda row: issue_sort_key(row))


def issue_sort_key(row):
	status_order = {"Open": 0, "Acknowledged": 1, "Resolved": 2}
	priority_order = {"Urgent": 0, "High": 1, "Normal": 2, "Low": 3}
	return (
		status_order.get(row.get("issue_status"), 9),
		priority_order.get(row.get("issue_priority"), 9),
	)


def get_recent_records(horse):
	return {
		"medical": frappe.get_all(
			"Horse Medical Record",
			filters={"horse": horse},
			fields=["name", "record_date", "record_type", "status", "summary"],
			order_by="record_date desc, creation desc",
			limit=3,
		),
		"training": frappe.get_all(
			"Horse Training Record",
			filters={"horse": horse},
			fields=["name", "training_date", "work_type", "outcome", "notes"],
			order_by="training_date desc, creation desc",
			limit=3,
		),
		"feeding": frappe.get_all(
			"Horse Feeding Record",
			filters={"horse": horse},
			fields=["name", "feeding_date", "item", "quantity", "unit", "notes"],
			order_by="feeding_date desc, feeding_time desc, creation desc",
			limit=3,
		),
	}


def get_upcoming_items(horse):
	return {
		"tasks": frappe.get_all(
			"Task",
			filters={
				"horse": horse,
				"owner_visible": 1,
				"status": "Open",
				"due_date": ["between", [today(), add_days(today(), 14)]],
			},
			fields=["name", "subject", "due_date", "task_type", "starts_on"],
			order_by="starts_on asc, due_date asc",
			limit=5,
		),
		"owner_tasks": frappe.get_all(
			"Owner Task",
			filters={
				"horse": horse,
				"status": "Open",
				"due_date": ["between", [today(), add_days(today(), 30)]],
			},
			fields=["name", "subject", "due_date", "task_type", "priority"],
			order_by="starts_on asc, due_date asc",
			limit=5,
		),
	}
