import frappe
from frappe import _
from frappe.utils import flt


CASH_ACCOUNT_BY_METHOD = {
	"Cash": "Cash",
	"Card": "Bank",
	"Bank Transfer": "Bank",
	"EFT": "Bank",
	"Cheque": "Bank",
	"Other": "Clearing",
}


def create_transaction_ledger_entries(transaction):
	created = []
	if frappe.db.exists(
		"Payment Ledger Entry",
		{"transaction_input": transaction.name, "direction": ["!=", "Reversal"]},
	):
		return created

	payment_account = transaction.payment_account or get_payment_account(transaction.payment_method)
	for line in transaction.lines:
		amount = flt(line.total)
		if not amount:
			continue

		line_account = getattr(line, "account", None) or get_line_account(transaction, line)
		if transaction.direction == "Money In":
			entries = [
				(payment_account, amount, 0),
				(line_account, 0, amount),
			]
		else:
			entries = [
				(line_account, amount, 0),
				(payment_account, 0, amount),
			]

		for account, debit, credit in entries:
			entry = make_ledger_entry(
				transaction=transaction,
				line=line,
				account=account,
				debit=debit,
				credit=credit,
				direction=transaction.direction,
			)
			created.append(entry.name)

	return created


def reverse_transaction_ledger_entries(transaction):
	entries = frappe.get_all(
		"Payment Ledger Entry",
		filters={
			"transaction_input": transaction.name,
			"direction": ["!=", "Reversal"],
		},
		fields=["name", "account", "debit", "credit"],
		order_by="creation asc",
	)
	created = []
	for entry in entries:
		if frappe.db.exists("Payment Ledger Entry", {"reversed_against": entry.name}):
			continue
		line = frappe._dict({"name": entry.name})
		reversal = make_ledger_entry(
			transaction=transaction,
			line=line,
			account=entry.account,
			debit=flt(entry.credit),
			credit=flt(entry.debit),
			direction="Reversal",
			reversed_against=entry.name,
			description=_("Reversal of {0}").format(entry.name),
		)
		created.append(reversal.name)
	return created


def make_ledger_entry(
	transaction,
	line,
	account,
	debit,
	credit,
	direction,
	reversed_against=None,
	description=None,
):
	entry = frappe.new_doc("Payment Ledger Entry")
	entry.posting_date = transaction.transaction_date
	entry.transaction_input = transaction.name
	entry.direction = direction
	entry.account = account
	entry.transaction_type = transaction.transaction_type
	entry.transaction_category = getattr(line, "cost_category", None) or transaction.transaction_category
	entry.party_type = transaction.party_type
	entry.vendor = transaction.vendor
	entry.horse_owner = transaction.horse_owner
	entry.groom_profile = transaction.groom_profile or getattr(line, "groom_profile", None)
	entry.line_type = getattr(line, "line_type", None)
	entry.item = getattr(line, "item", None)
	entry.horse = getattr(line, "horse", None)
	entry.tournament = getattr(line, "tournament", None)
	entry.reference_doctype = getattr(line, "reference_doctype", None)
	entry.reference_name = getattr(line, "reference_name", None)
	entry.description = description or getattr(line, "description", None)
	entry.debit = flt(debit)
	entry.credit = flt(credit)
	entry.currency = transaction.currency
	entry.voucher_type = transaction.doctype
	entry.voucher_no = transaction.name
	entry.voucher_detail_no = getattr(line, "name", None)
	entry.reversed_against = reversed_against
	entry.insert(ignore_permissions=True)
	return entry


def get_payment_account(payment_method):
	account_name = CASH_ACCOUNT_BY_METHOD.get(payment_method) or "Clearing"
	return ensure_money_account(account_name, "Asset", is_cash_account=1)


def get_line_account(transaction, line):
	category = getattr(line, "cost_category", None) or transaction.transaction_category or "Other"
	if transaction.direction == "Money In":
		return ensure_money_account(f"Income - {category}", "Income")
	return ensure_money_account(f"Expense - {category}", "Expense")


def ensure_money_account(account_name, account_type, is_cash_account=0):
	if frappe.db.exists("Money Account", account_name):
		return account_name

	account = frappe.new_doc("Money Account")
	account.account_name = account_name
	account.account_type = account_type
	account.root_type = "Debit" if account_type in ("Asset", "Expense") else "Credit"
	account.is_cash_account = is_cash_account
	account.is_active = 1
	account.insert(ignore_permissions=True)
	return account.name


def backfill_transaction_ledger_entries():
	if not frappe.db.table_exists("Payment Ledger Entry") or not frappe.db.table_exists("Transaction Input"):
		return []

	created = []
	if frappe.db.has_column("Transaction Input", "payment_record"):
		frappe.db.sql(
			"""
			update `tabTransaction Input`
			set docstatus = 1, status = 'Posted'
			where docstatus = 0
				and status = 'Posted'
				and ifnull(payment_record, '') != ''
			"""
		)

	if frappe.db.has_column("Payment Ledger Entry", "source_transaction"):
		frappe.db.sql(
			"""
			update `tabPayment Ledger Entry`
			set transaction_input = source_transaction
			where ifnull(transaction_input, '') = ''
				and ifnull(source_transaction, '') != ''
			"""
		)

	rebuild_legacy_single_entry_ledgers()

	for transaction_name in frappe.get_all("Transaction Input", filters={"docstatus": 1}, pluck="name"):
		if frappe.db.exists("Payment Ledger Entry", {"transaction_input": transaction_name}):
			continue
		transaction = frappe.get_doc("Transaction Input", transaction_name)
		created.extend(create_transaction_ledger_entries(transaction))

	return created


def rebuild_legacy_single_entry_ledgers():
	if not frappe.db.has_column("Payment Ledger Entry", "account"):
		return

	transaction_names = frappe.get_all(
		"Payment Ledger Entry",
		filters={
			"transaction_input": ["is", "set"],
			"account": ["is", "not set"],
		},
		pluck="transaction_input",
		distinct=True,
	)

	for transaction_name in transaction_names:
		if not frappe.db.exists("Transaction Input", transaction_name):
			continue
		for entry_name in frappe.get_all(
			"Payment Ledger Entry",
			filters={"transaction_input": transaction_name},
			pluck="name",
		):
			frappe.delete_doc("Payment Ledger Entry", entry_name, ignore_permissions=True, force=True)

		transaction = frappe.get_doc("Transaction Input", transaction_name)
		if transaction.docstatus == 1:
			create_transaction_ledger_entries(transaction)
