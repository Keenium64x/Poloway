import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate


class VendorQuote(Document):
	def validate(self):
		if not self.quote_date:
			self.quote_date = getdate()
		self.calculate_totals()

	def calculate_totals(self):
		total = 0
		for line in self.lines:
			line.quantity = flt(line.quantity) or 1
			line.total = flt(line.quantity) * flt(line.rate) + flt(line.tax_amount)
			total += flt(line.total)
		self.total_amount = total


@frappe.whitelist()
def create_transaction_input(quote):
	doc = frappe.get_doc("Vendor Quote", quote)
	doc.check_permission("read")
	if doc.status != "Selected":
		doc.status = "Selected"
		doc.save(ignore_permissions=True)

	transaction = frappe.new_doc("Transaction Input")
	transaction.transaction_type = "Purchase"
	transaction.transaction_category = infer_category(doc)
	transaction.party_type = "Vendor"
	transaction.vendor = doc.vendor
	transaction.transaction_date = getdate()
	transaction.selected_quote = doc.name
	transaction.receipt_file = doc.quote_file
	transaction.currency = doc.currency
	transaction.notes = doc.notes

	for line in doc.lines:
		transaction.append("lines", {
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

	transaction.insert(ignore_permissions=True)
	return transaction.name


@frappe.whitelist()
def select_quote(quote, reject_competing=1):
	doc = frappe.get_doc("Vendor Quote", quote)
	doc.check_permission("write")
	doc.status = "Selected"
	doc.save(ignore_permissions=True)

	if reject_competing:
		reject_competing_quotes(doc)

	return doc.name


def reject_competing_quotes(doc):
	filters = {
		"name": ["!=", doc.name],
		"status": ["in", ["Draft", "Submitted"]],
	}
	if doc.linked_horse:
		filters["linked_horse"] = doc.linked_horse
	elif doc.tournament:
		filters["tournament"] = doc.tournament
	else:
		return

	for quote_name in frappe.get_all("Vendor Quote", filters=filters, pluck="name"):
		frappe.db.set_value("Vendor Quote", quote_name, "status", "Rejected")


def infer_category(quote):
	for line in quote.lines:
		if line.line_type == "Horse":
			return "Horse Purchase"
		if line.line_type == "Tournament":
			return "Tournament"
		if line.line_type == "Item":
			return "Feed" if line.cost_category == "Feed" else "Equipment"
	return "Other"
