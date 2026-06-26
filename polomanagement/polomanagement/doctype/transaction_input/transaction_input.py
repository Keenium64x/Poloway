import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class TransactionInput(Document):
	def validate(self):
		self.validate_not_posted()
		if not self.transaction_date:
			self.transaction_date = getdate()
		self.set_direction()
		self.calculate_totals()

	def validate_not_posted(self):
		if self.is_new():
			return
		before = self.get_doc_before_save()
		if before and before.payment_record:
			frappe.throw(_("Posted transaction inputs cannot be edited. Create a reversal or a new transaction instead."))

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

	def create_payment_record(self):
		if self.payment_record:
			return frappe.get_doc("Payment Record", self.payment_record)

		if not self.lines:
			frappe.throw(_("Add at least one transaction line before creating a payment record."))

		payment = frappe.new_doc("Payment Record")
		payment.posting_date = self.transaction_date or getdate()
		payment.direction = self.direction
		payment.transaction_type = self.transaction_type
		payment.transaction_category = self.transaction_category
		payment.party_type = self.party_type
		payment.vendor = self.vendor
		payment.horse_owner = self.horse_owner
		payment.source_transaction = self.name
		payment.selected_quote = self.selected_quote
		payment.receipt_file = self.receipt_file
		payment.currency = self.currency
		payment.payment_method = self.payment_method
		payment.notes = self.notes

		for line in self.lines:
			payment.append("lines", {
				"line_type": line.line_type,
				"item": line.item,
				"horse": line.horse,
				"tournament": line.tournament,
				"description": line.description,
				"quantity": line.quantity,
				"unit": line.unit,
				"rate": line.rate,
				"tax_amount": line.tax_amount,
				"total": line.total,
				"cost_category": line.cost_category,
				"affects_inventory": line.affects_inventory,
			})

		payment.insert(ignore_permissions=True)
		payment.flags.ignore_permissions = True
		payment.submit()
		self.db_set({
			"payment_record": payment.name,
			"status": "Posted",
		})
		return payment


@frappe.whitelist()
def create_payment_record(transaction_input):
	doc = frappe.get_doc("Transaction Input", transaction_input)
	doc.check_permission("write")
	payment = doc.create_payment_record()
	return payment.name


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
		doc.append("lines", {
			"line_type": line.line_type,
			"item": line.item,
			"horse": line.horse,
			"tournament": line.tournament,
			"description": line.description,
			"quantity": line.quantity,
			"unit": line.unit,
			"rate": line.rate,
			"tax_amount": line.tax_amount,
			"cost_category": line.cost_category,
			"affects_inventory": line.affects_inventory,
		})
	doc.save(ignore_permissions=True)
	return doc.name
