import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class Purchase(Document):
	def validate(self):
		if not self.purchase_date:
			self.purchase_date = getdate()
		self.calculate_totals()
		if self.transaction_input and frappe.db.get_value("Transaction Input", self.transaction_input, "docstatus") == 1:
			self.status = "Posted"
		elif self.selected_quote:
			self.status = "Selected"

	def before_submit(self):
		if self.status == "Draft":
			self.status = "Open"

	def on_cancel(self):
		self.db_set("status", "Cancelled")

	def calculate_totals(self):
		total = 0
		for line in self.lines:
			line.quantity = flt(line.quantity) or 1
			line.total = flt(line.quantity) * flt(line.rate) + flt(line.tax_amount)
			total += flt(line.total)
		self.estimated_total = total


@frappe.whitelist()
def create_vendor_quote(purchase, vendor):
	doc = frappe.get_doc("Purchase", purchase)
	doc.check_permission("read")
	if not vendor:
		frappe.throw(_("Select a vendor first."))

	quote = frappe.new_doc("Vendor Quote")
	quote.quote_title = _("{0} quote").format(doc.purchase_title or doc.name)
	quote.vendor = vendor
	quote.status = "Draft"
	quote.quote_date = getdate()
	quote.currency = doc.currency
	quote.purchase = doc.name
	quote.linked_horse = doc.linked_horse
	quote.tournament = doc.tournament
	quote.notes = doc.notes

	for line in doc.lines:
		quote.append(
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

	quote.insert(ignore_permissions=True)
	if doc.status in ("Draft", "Open"):
		doc.db_set("status", "Quoted")
	return quote.name


@frappe.whitelist()
def create_transaction_from_selected_quote(purchase, submit_transaction=0, post_payment=0):
	doc = frappe.get_doc("Purchase", purchase)
	doc.check_permission("write")
	if not doc.selected_quote:
		frappe.throw(_("Select a quote before creating a transaction."))

	from polomanagement.polomanagement.doctype.vendor_quote.vendor_quote import create_transaction_input

	transaction_name = create_transaction_input(doc.selected_quote)
	transaction = frappe.get_doc("Transaction Input", transaction_name)
	doc.db_set("transaction_input", transaction.name)

	if submit_transaction or post_payment:
		transaction.submit()
		doc.db_set("status", "Posted")
		return {"transaction_input": transaction.name}

	doc.db_set("status", "Selected")
	return {"transaction_input": transaction.name}
