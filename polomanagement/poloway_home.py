from __future__ import annotations

import frappe
from frappe.utils import add_days, flt, get_first_day, getdate, today


@frappe.whitelist()
def get_home_data():
	return {
		"summary": get_summary(),
		"horses": get_horses(),
		"today": get_today_items(),
		"upcoming": get_upcoming_items(),
		"care": get_care_snapshot(),
		"money": get_money_snapshot(),
		"matches": get_match_snapshot(),
		"quick_actions": get_quick_actions(),
	}


def get_summary():
	return {
		"horses": frappe.db.count("Horse"),
		"available_horses": frappe.db.count("Horse", {"availability_status": "Available"}),
		"today_tasks": frappe.db.count("Task", today_task_filters("Open")),
		"owner_actions": frappe.db.count(
			"Owner Task",
			{"status": "Open", "due_date": ["between", [today(), add_days(today(), 14)]]},
		),
		"open_issues": frappe.db.count(
			"Task",
			{"issue_reported": 1, "issue_status": ["in", ["Open", "Acknowledged"]]},
		),
	}


def get_horses():
	fields = [
		"name",
		"name1",
		"sex",
		"colour",
		"current_location",
		"stable_number",
		"playing_status",
		"availability_status",
	]
	horses = frappe.get_all(
		"Horse",
		fields=fields,
		order_by="modified desc",
		limit_page_length=8,
	)
	for horse in horses:
		horse["display_name"] = horse.get("name1") or horse.get("name")
		horse["open_tasks"] = frappe.db.count(
			"Task", {"horse": horse.name, "owner_visible": 1, "status": "Open"}
		)
		horse["open_issues"] = frappe.db.count(
			"Task",
			{"horse": horse.name, "owner_visible": 1, "issue_reported": 1, "issue_status": ["!=", "Resolved"]},
		)
	return horses


def get_today_items():
	items = []
	for task in frappe.get_all(
		"Task",
		fields=["name", "subject", "task_type", "horse", "starts_on", "ends_on", "status"],
		filters=today_task_filters("Open"),
		order_by="starts_on asc, modified desc",
		limit_page_length=8,
	):
		items.append(
			{
				"doctype": "Task",
				"name": task.name,
				"title": task.subject,
				"type": task.task_type,
				"horse": task.horse,
				"starts_on": task.starts_on,
				"ends_on": task.ends_on,
				"status": task.status,
			}
		)
	for owner_task in frappe.get_all(
		"Owner Task",
		fields=["name", "subject", "task_type", "horse", "starts_on", "ends_on", "priority", "status"],
		filters={"status": "Open", "due_date": today()},
		order_by="starts_on asc, modified desc",
		limit_page_length=8,
	):
		items.append(
			{
				"doctype": "Owner Task",
				"name": owner_task.name,
				"title": owner_task.subject,
				"type": owner_task.task_type,
				"horse": owner_task.horse,
				"starts_on": owner_task.starts_on,
				"ends_on": owner_task.ends_on,
				"priority": owner_task.priority,
				"status": owner_task.status,
			}
		)
	return sorted(items, key=lambda row: str(row.get("starts_on") or ""))[:10]


def get_upcoming_items():
	return frappe.get_all(
		"Owner Task",
		fields=["name", "subject", "task_type", "horse", "due_date", "priority", "status"],
		filters={"status": "Open", "due_date": ["between", [add_days(today(), 1), add_days(today(), 14)]]},
		order_by="due_date asc, priority desc",
		limit_page_length=8,
	)


def get_care_snapshot():
	return {
		"feeding_7d": count_since("Horse Feeding Record", "feeding_date", 7),
		"training_7d": count_since("Horse Training Record", "training_date", 7),
		"medical_30d": count_since("Horse Medical Record", "record_date", 30),
		"compliance_due": len(get_compliance_due_horses()),
	}


def get_money_snapshot():
	current = getdate(today())
	start = get_first_day(current)
	entries = frappe.get_all(
		"Payment Ledger Entry",
		fields=["direction", "debit", "credit"],
		filters={"posting_date": ["between", [start, current]], "docstatus": 1},
		limit_page_length=500,
	)
	income = sum(flt(row.credit) for row in entries if row.direction == "Money In")
	outflow = sum(flt(row.debit) for row in entries if row.direction == "Money Out")
	return {
		"income": income,
		"outflow": outflow,
		"net": income - outflow,
		"unposted": frappe.db.count("Transaction Input", {"docstatus": 0, "status": ["!=", "Reversed"]}),
	}


def get_match_snapshot():
	return {
		"upcoming": frappe.get_all(
			"Match Day",
			fields=["name", "event_name", "match_date", "venue", "status"],
			filters={"match_date": [">=", today()], "status": ["!=", "Cancelled"]},
			order_by="match_date asc",
			limit_page_length=4,
		),
	}


def get_quick_actions():
	return [
		{"label": "Add Horse", "route": ["Form", "Horse", "new-horse"], "icon": "horse"},
		{"label": "Add Owner Task", "route": ["Form", "Owner Task", "new-owner-task"], "icon": "calendar"},
		{"label": "Log Care", "route": ["Form", "Horse Care Entry", "new-horse-care-entry"], "icon": "heart"},
		{"label": "Upload Receipt", "route": ["Form", "Receipt Import", "new-receipt-import"], "icon": "receipt"},
	]


def today_task_filters(status):
	day_start = f"{today()} 00:00:00"
	day_end = f"{today()} 23:59:59"
	return {
		"owner_visible": 1,
		"status": status,
		"starts_on": ["<=", day_end],
		"ends_on": [">=", day_start],
	}


def count_since(doctype, date_field, days):
	return frappe.db.count(doctype, {date_field: [">=", add_days(today(), -days)]})


def get_compliance_due_horses():
	return frappe.get_all(
		"Horse Medical Record",
		filters={"next_due_date": ["between", [today(), add_days(today(), 14)]]},
		pluck="horse",
		distinct=True,
	)
