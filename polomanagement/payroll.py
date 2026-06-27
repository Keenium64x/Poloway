import calendar

import frappe
from frappe import _
from frappe.utils import cint, flt, getdate, today


def generate_due_groom_payments():
	settings = frappe.get_single("Autopayments")
	if not settings.enabled:
		return []

	current = getdate(today())
	period = current.strftime("%Y-%m")
	created = []

	for rule in settings.rules:
		if not rule.enabled or rule.rule_type != "Groom Salary" or not rule.groom_profile:
			continue
		if rule.last_generated_for == period:
			continue
		if current.day != payable_day(current.year, current.month, rule.day_of_month):
			continue

		groom = frappe.get_doc("Groom Profile", rule.groom_profile)
		if not flt(groom.salary):
			continue

		transaction = create_groom_salary_transaction(groom, current, period)
		if rule.submit_automatically:
			transaction.submit()
		created.append({"transaction_input": transaction.name, "submitted": transaction.docstatus == 1})

		rule.last_generated_for = period

	if created:
		settings.save(ignore_permissions=True)

	return created


def payable_day(year, month, configured_day):
	last_day = calendar.monthrange(year, month)[1]
	day = cint(configured_day) or 25
	return min(max(day, 1), last_day)


def create_groom_salary_transaction(groom, posting_date, period):
	transaction = frappe.new_doc("Transaction Input")
	transaction.transaction_type = "Expense"
	transaction.transaction_category = "Groom Salary"
	transaction.transaction_date = posting_date
	transaction.party_type = "Groom"
	transaction.groom_profile = groom.name
	transaction.payment_method = "EFT"
	transaction.notes = f"Groom salary for {groom.groom_name or groom.name} ({period})."
	transaction.append(
		"lines",
		{
			"line_type": "Groom",
			"groom_profile": groom.name,
			"description": f"Salary for {groom.groom_name or groom.name} ({period})",
			"quantity": 1,
			"rate": flt(groom.salary),
			"cost_category": "Groom Salary",
			"affects_inventory": 0,
		},
	)
	transaction.insert(ignore_permissions=True)
	return transaction


@frappe.whitelist()
def create_salary_transaction(groom_profile, posting_date=None, submit_transaction=0):
	groom = frappe.get_doc("Groom Profile", groom_profile)
	groom.check_permission("read")

	if not flt(groom.salary):
		frappe.throw(_("Set a salary on the groom profile before creating a salary transaction."))

	posting_date = getdate(posting_date or today())
	period = posting_date.strftime("%Y-%m")
	transaction = create_groom_salary_transaction(groom, posting_date, period)

	if cint(submit_transaction):
		transaction.submit()

	return {"transaction_input": transaction.name, "submitted": transaction.docstatus == 1}
