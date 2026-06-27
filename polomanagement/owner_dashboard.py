import frappe
from frappe import _
from frappe.utils import add_days, add_months, flt, get_first_day, getdate, today


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
		"operations": get_horse_operations(horse),
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
		"compliance_due": count_horse_compliance_due(horse),
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
	conditions = ["tx.docstatus = 1", "line.horse = %(horse)s"]
	values = {"horse": horse}
	if from_date:
		conditions.append("tx.transaction_date >= %(from_date)s")
		values["from_date"] = from_date
	if direction:
		conditions.append("tx.direction = %(direction)s")
		values["direction"] = direction

	result = frappe.db.sql(
		f"""
		select sum(line.total)
		from `tabTransaction Input Line` line
		inner join `tabTransaction Input` tx on tx.name = line.parent
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
		where tx.docstatus = 0
			and tx.status != 'Reversed'
			and line.horse = %(horse)s
		""",
		{"horse": horse},
	)


def get_recent_horse_payments(horse):
	return frappe.db.sql(
		"""
		select
			payment.name,
			payment.transaction_date as posting_date,
			payment.direction,
			payment.transaction_category,
			payment.vendor,
			line.description,
			line.total
		from `tabTransaction Input Line` line
		inner join `tabTransaction Input` payment on payment.name = line.parent
		where payment.docstatus = 1
			and line.horse = %(horse)s
		order by payment.transaction_date desc, payment.creation desc, line.idx asc
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


def get_horse_operations(horse):
	return {
		"tack": frappe.get_all(
			"Horse Tack Configuration",
			filters={"horse": horse, "is_active": 1},
			fields=["name", "configuration_name", "bit", "martingale", "prep_instructions"],
			order_by="modified desc",
			limit=3,
		),
		"matches": get_upcoming_match_days(horse),
		"travel": get_upcoming_travel(horse),
		"compliance": get_horse_compliance_due(horse),
	}


def get_upcoming_match_days(horse):
	return frappe.db.sql(
		"""
		select
			match_day.name,
			match_day.event_name,
			match_day.match_date,
			match_day.venue,
			chukker.chukker_number,
			chukker.status
		from `tabChukker Assignment` chukker
		inner join `tabMatch Day` match_day on match_day.name = chukker.parent
		where chukker.horse = %(horse)s
			and match_day.match_date >= %(today)s
			and match_day.status != 'Cancelled'
		order by match_day.match_date asc, chukker.chukker_number asc
		limit 5
		""",
		{"horse": horse, "today": today()},
		as_dict=True,
	)


def get_upcoming_travel(horse):
	return frappe.db.sql(
		"""
		select
			manifest.name,
			manifest.trip_name,
			manifest.departure_date,
			manifest.destination,
			manifest.status,
			row.trailer_position,
			row.paperwork_status
		from `tabTravel Manifest Horse` row
		inner join `tabTravel Manifest` manifest on manifest.name = row.parent
		where row.horse = %(horse)s
			and manifest.departure_date >= %(today)s
			and manifest.status != 'Cancelled'
		order by manifest.departure_date asc, manifest.creation desc
		limit 5
		""",
		{"horse": horse, "today": today()},
		as_dict=True,
	)


def get_horse_compliance_due(horse):
	return frappe.db.sql(
		"""
		select name, record_type, summary, next_due_date
		from `tabHorse Medical Record`
		where horse = %(horse)s
			and next_due_date is not null
			and next_due_date <= %(due_by)s
		order by next_due_date asc, creation desc
		limit 5
		""",
		{"horse": horse, "due_by": add_days(getdate(), 30)},
		as_dict=True,
	)


def count_horse_compliance_due(horse):
	result = frappe.db.sql(
		"""
		select count(*)
		from `tabHorse Medical Record`
		where horse = %(horse)s
			and next_due_date is not null
			and next_due_date <= %(due_by)s
		""",
		{"horse": horse, "due_by": add_days(getdate(), 30)},
	)
	return result[0][0] if result else 0


def count_since(doctype, date_field, horse, days):
	return frappe.db.count(
		doctype,
		{
			"horse": horse,
			date_field: [">=", add_days(getdate(), -days)],
		},
	)


@frappe.whitelist()
def get_owner_home_dashboard():
	ensure_owner_dashboard_access()
	return {
		"financial": get_financial_snapshot(),
		"polo": get_polo_snapshot(),
		"horses": get_horse_performance_snapshot(),
		"actions": get_owner_action_snapshot(),
	}


@frappe.whitelist()
def get_money_dashboard():
	ensure_owner_dashboard_access()
	return {
		"financial": get_financial_snapshot(),
		"operations": get_money_operations_snapshot(),
		"inventory": get_inventory_snapshot(),
		"vendors": get_vendor_snapshot(),
	}


def ensure_owner_dashboard_access():
	if frappe.session.user == "Guest":
		frappe.throw(_("Login required."), frappe.PermissionError)

	allowed_roles = {"Horse Owner", "Stable Manager", "System Manager"}
	if not allowed_roles.intersection(set(frappe.get_roles())):
		frappe.throw(_("You do not have access to this dashboard."), frappe.PermissionError)


def get_financial_snapshot():
	current = getdate(today())
	month_start = get_first_day(current)
	year_start = f"{current.year}-01-01"
	return {
		"month": get_financial_totals(month_start, current),
		"year": get_financial_totals(year_start, current),
		"unposted": frappe.db.count("Transaction Input", {"docstatus": 0, "status": ["!=", "Reversed"]}),
		"open_purchases": frappe.db.count("Purchase", {"status": ["in", ["Open", "Quoted", "Selected"]]}),
		"trend": get_financial_trend(),
		"categories": get_financial_categories(),
		"recent": get_recent_transactions(),
	}


def get_financial_totals(from_date, to_date):
	rows = frappe.db.sql(
		"""
		select
			tx.direction,
			sum(line.total) as total
		from `tabTransaction Input` tx
		inner join `tabTransaction Input Line` line on line.parent = tx.name
		where tx.docstatus = 1
			and tx.transaction_date between %(from_date)s and %(to_date)s
		group by tx.direction
		""",
		{"from_date": from_date, "to_date": to_date},
		as_dict=True,
	)
	income = sum(flt(row.total) for row in rows if row.direction == "Money In")
	outflow = sum(flt(row.total) for row in rows if row.direction == "Money Out")
	return {"income": income, "outflow": outflow, "net": income - outflow}


def get_financial_trend():
	start_date = get_first_day(add_months(getdate(today()), -5))
	rows = frappe.db.sql(
		"""
		select
			date_format(tx.transaction_date, '%%Y-%%m') as period,
			tx.direction,
			sum(line.total) as total
		from `tabTransaction Input` tx
		inner join `tabTransaction Input Line` line on line.parent = tx.name
		where tx.docstatus = 1
			and tx.transaction_date >= %(start_date)s
		group by period, tx.direction
		order by period asc
		""",
		{"start_date": start_date},
		as_dict=True,
	)
	periods = []
	cursor = start_date
	for _index in range(6):
		periods.append(cursor.strftime("%Y-%m"))
		cursor = add_months(cursor, 1)

	trend = {period: {"period": period, "income": 0, "outflow": 0, "net": 0} for period in periods}
	for row in rows:
		if row.period not in trend:
			continue
		if row.direction == "Money In":
			trend[row.period]["income"] = flt(row.total)
		else:
			trend[row.period]["outflow"] = flt(row.total)

	for period in trend:
		trend[period]["net"] = trend[period]["income"] - trend[period]["outflow"]
	return list(trend.values())


def get_financial_categories():
	rows = frappe.db.sql(
		"""
		select
			coalesce(line.cost_category, tx.transaction_category, 'Other') as category,
			tx.direction,
			sum(line.total) as total
		from `tabTransaction Input` tx
		inner join `tabTransaction Input Line` line on line.parent = tx.name
		where tx.docstatus = 1
			and tx.transaction_date >= %(from_date)s
		group by category, tx.direction
		order by total desc
		limit 8
		""",
		{"from_date": add_days(getdate(today()), -90)},
		as_dict=True,
	)
	return rows


def get_recent_transactions(limit=5):
	return frappe.get_all(
		"Transaction Input",
		filters={"docstatus": 1},
		fields=["name", "transaction_date", "transaction_type", "transaction_category", "direction", "total_amount"],
		order_by="transaction_date desc, creation desc",
		limit=limit,
	)


def get_polo_snapshot():
	return {
		"next_match": get_next_match(),
		"upcoming": frappe.get_all(
			"Match Day",
			filters={"match_date": [">=", today()], "status": ["!=", "Cancelled"]},
			fields=["name", "event_name", "match_date", "venue", "status", "team", "opponent"],
			order_by="match_date asc, creation desc",
			limit=6,
		),
		"recent": frappe.get_all(
			"Match Day",
			filters={"match_date": ["<", today()]},
			fields=["name", "event_name", "match_date", "venue", "status", "team", "opponent"],
			order_by="match_date desc, creation desc",
			limit=4,
		),
		"status_counts": get_match_status_counts(),
		"horse_usage": get_match_horse_usage(),
	}


def get_next_match():
	rows = frappe.get_all(
		"Match Day",
		filters={"match_date": [">=", today()], "status": ["!=", "Cancelled"]},
		fields=["name", "event_name", "match_date", "venue", "status", "team", "opponent"],
		order_by="match_date asc, creation desc",
		limit=1,
	)
	return rows[0] if rows else None


def get_match_status_counts():
	return frappe.db.sql(
		"""
		select status, count(*) as count
		from `tabMatch Day`
		where match_date >= %(from_date)s
		group by status
		order by count desc
		""",
		{"from_date": add_days(getdate(today()), -180)},
		as_dict=True,
	)


def get_match_horse_usage():
	return frappe.db.sql(
		"""
		select
			chukker.horse,
			coalesce(horse.name1, chukker.horse) as horse_name,
			count(*) as chukkers
		from `tabChukker Assignment` chukker
		inner join `tabMatch Day` match_day on match_day.name = chukker.parent
		left join `tabHorse` horse on horse.name = chukker.horse
		where match_day.match_date >= %(from_date)s
			and match_day.status != 'Cancelled'
		group by chukker.horse, horse.name1
		order by chukkers desc
		limit 6
		""",
		{"from_date": add_days(getdate(today()), -180)},
		as_dict=True,
	)


def get_horse_performance_snapshot():
	return {
		"counts": {
			"total": frappe.db.count("Horse"),
			"available": frappe.db.count("Horse", {"availability_status": "Available"}),
			"attention": horses_needing_attention().get("value"),
			"training_30d": frappe.db.count(
				"Horse Training Record",
				{"training_date": [">=", add_days(getdate(today()), -30)]},
			),
		},
		"top_training": get_top_training_horses(),
		"readiness": get_horse_readiness_counts(),
		"issues": get_owner_issues(limit=5),
	}


def get_top_training_horses():
	return frappe.db.sql(
		"""
		select
			record.horse,
			coalesce(horse.name1, record.horse) as horse_name,
			count(*) as sessions,
			sum(case when record.outcome = 'Completed' then 1 else 0 end) as completed,
			sum(case when record.outcome = 'Needs Follow Up' then 1 else 0 end) as follow_up
		from `tabHorse Training Record` record
		left join `tabHorse` horse on horse.name = record.horse
		where record.training_date >= %(from_date)s
		group by record.horse, horse.name1
		order by completed desc, sessions desc
		limit 6
		""",
		{"from_date": add_days(getdate(today()), -60)},
		as_dict=True,
	)


def get_horse_readiness_counts():
	return frappe.db.sql(
		"""
		select coalesce(availability_status, 'Not Set') as status, count(*) as count
		from `tabHorse`
		group by availability_status
		order by count desc
		""",
		as_dict=True,
	)


def get_owner_issues(limit=5):
	return frappe.get_all(
		"Task",
		filters={"owner_visible": 1, "issue_reported": 1, "issue_status": ["!=", "Resolved"]},
		fields=["name", "subject", "horse", "due_date", "issue_priority", "issue_status", "completion_notes"],
		order_by="modified desc",
		limit=limit,
	)


def get_owner_action_snapshot():
	return {
		"open_tasks": frappe.get_all(
			"Owner Task",
			filters={"status": "Open"},
			fields=["name", "subject", "due_date", "priority", "task_type", "horse", "tournament"],
			order_by="due_date asc, starts_on asc",
			limit=6,
		),
		"open_issues": get_owner_issues(limit=6),
		"groom_today": {
			"open": today_open_tasks().get("value"),
			"completed": today_completed_tasks().get("value"),
		},
	}


def get_money_operations_snapshot():
	return {
		"unposted": frappe.get_all(
			"Transaction Input",
			filters={"docstatus": 0, "status": ["!=", "Reversed"]},
			fields=["name", "transaction_date", "transaction_type", "transaction_category", "total_amount"],
			order_by="transaction_date desc, creation desc",
			limit=6,
		),
		"purchases": frappe.get_all(
			"Purchase",
			filters={"status": ["in", ["Open", "Quoted", "Selected"]]},
			fields=["name", "purchase_title", "status", "needed_by", "estimated_total", "linked_horse"],
			order_by="needed_by asc, creation desc",
			limit=6,
		),
		"quotes": frappe.get_all(
			"Vendor Quote",
			filters={"status": ["in", ["Draft", "Submitted", "Selected"]]},
			fields=["name", "quote_title", "vendor", "status", "quote_date", "valid_until", "total_amount"],
			order_by="quote_date desc, total_amount asc",
			limit=6,
		),
	}


def get_inventory_snapshot():
	return {
		"items": frappe.db.count("Item"),
		"locations": frappe.db.count("Inventory Location"),
		"categories": frappe.db.count("Item Category"),
		"recent_stock": frappe.get_all(
			"Item Stock Ledger",
			fields=["name", "item", "posting_date", "movement_type", "quantity_change", "quantity_after"],
			order_by="posting_date desc, creation desc",
			limit=6,
		),
	}


def get_vendor_snapshot():
	return {
		"vendors": frappe.db.count("Vendor"),
		"active_quotes": frappe.db.count("Vendor Quote", {"status": ["in", ["Draft", "Submitted", "Selected"]]}),
		"recent_vendors": frappe.get_all(
			"Vendor",
			fields=["name", "vendor_name", "vendor_type", "phone", "email"],
			order_by="modified desc",
			limit=5,
		),
	}


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
