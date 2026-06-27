import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class TransactionInput(Document):
	def validate(self):
		if not self.transaction_date:
			self.transaction_date = getdate()
		self.set_direction()
		self.calculate_totals()

	def before_submit(self):
		if not self.lines:
			frappe.throw(_("Add at least one transaction detail before submitting."))
		self.status = "Posted"

	def on_submit(self):
		self.update_inventory()
		self.create_ledger_entries()
		self.db_set("status", "Posted")

	def on_cancel(self):
		self.reverse_inventory()
		self.reverse_ledger_entries()
		self.db_set("status", "Reversed")
		if self.selected_quote:
			purchase = frappe.db.get_value("Vendor Quote", self.selected_quote, "purchase")
			if purchase:
				frappe.db.set_value("Purchase", purchase, "status", "Selected")

	def set_direction(self):
		if self.transaction_type in ("Sale", "Income"):
			self.direction = "Money In"
		else:
			self.direction = "Money Out"

	def calculate_totals(self):
		total = 0
		for line in self.lines:
			line.quantity = flt(line.quantity) or 1
			line.total = flt(line.quantity) * flt(line.rate) + flt(line.tax_amount)
			total += flt(line.total)
		self.total_amount = total

	def update_inventory(self):
		from polomanagement.polomanagement.stock_ledger import create_item_stock_ledger_entry

		for line in self.lines:
			if not should_update_inventory(line):
				continue
			quantity_change = get_quantity_change(line.quantity, self.transaction_type)
			if not quantity_change:
				continue
			create_item_stock_ledger_entry(
				item=line.item,
				quantity_change=quantity_change,
				valuation_rate=line.rate,
				movement_type=get_movement_type(self.transaction_type),
				voucher_type=self.doctype,
				voucher_no=self.name,
				voucher_detail_no=line.name,
				posting_date=self.transaction_date,
				remarks=line.description,
			)

	def reverse_inventory(self):
		from polomanagement.polomanagement.stock_ledger import reverse_stock_ledger_entries

		reverse_stock_ledger_entries(self.doctype, self.name, self.transaction_date)

	def create_ledger_entries(self):
		from polomanagement.polomanagement.payment_ledger import create_transaction_ledger_entries

		create_transaction_ledger_entries(self)

	def reverse_ledger_entries(self):
		from polomanagement.polomanagement.payment_ledger import reverse_transaction_ledger_entries

		reverse_transaction_ledger_entries(self)

	def post_transaction(self):
		if self.docstatus == 1:
			return self
		self.submit()
		return self


def should_update_inventory(line):
	return line.line_type == "Item" and line.item and line.affects_inventory


def get_quantity_change(quantity, transaction_type):
	qty = flt(quantity)
	if transaction_type == "Sale":
		return qty * -1
	elif transaction_type not in ("Purchase", "Sale"):
		return 0
	return qty


def get_movement_type(transaction_type):
	if transaction_type == "Sale":
		return "Sale Issue"
	return "Purchase Receipt"


@frappe.whitelist()
def submit_transaction(transaction_input):
	doc = frappe.get_doc("Transaction Input", transaction_input)
	doc.check_permission("submit")
	doc.post_transaction()
	return doc.name


@frappe.whitelist()
def pull_quote_lines(transaction_input):
	doc = frappe.get_doc("Transaction Input", transaction_input)
	doc.check_permission("write")

	if not doc.selected_quote:
		frappe.throw(_("Select a vendor quote first."))

	quote = frappe.get_doc("Vendor Quote", doc.selected_quote)
	doc.vendor = quote.vendor
	doc.receipt_file = quote.quote_file
	doc.currency = quote.currency
	doc.lines = []
	for line in quote.lines:
		doc.append(
			"lines",
			{
				"line_type": line.line_type,
				"item": line.item,
				"horse": line.horse,
				"groom_profile": line.groom_profile,
				"tournament": line.tournament,
				"reference_doctype": line.reference_doctype,
				"reference_name": line.reference_name,
				"description": line.description,
				"quantity": line.quantity,
				"unit": line.unit,
				"rate": line.rate,
				"tax_amount": line.tax_amount,
				"cost_category": line.cost_category,
				"affects_inventory": line.affects_inventory,
			},
		)
	doc.save(ignore_permissions=True)
	return doc.name
