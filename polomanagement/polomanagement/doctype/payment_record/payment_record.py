import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class PaymentRecord(Document):
	def validate(self):
		if not self.posting_date:
			self.posting_date = getdate()
		self.calculate_totals()

	def before_submit(self):
		self.status = "Posted"

	def on_submit(self):
		self.update_inventory()

	def on_cancel(self):
		self.reverse_inventory()
		self.db_set("status", "Reversed")

	def calculate_totals(self):
		total = 0
		for line in self.lines:
			line.quantity = flt(line.quantity) or 1
			line.total = flt(line.quantity) * flt(line.rate) + flt(line.tax_amount)
			total += flt(line.total)
		self.total_amount = total

	def update_inventory(self):
		for line in self.lines:
			if not should_update_inventory(line):
				continue
			apply_item_movement(line.item, line.quantity, line.rate, self.transaction_type)

	def reverse_inventory(self):
		for line in self.lines:
			if not should_update_inventory(line):
				continue
			apply_item_movement(line.item, line.quantity * -1, line.rate, self.transaction_type)


def should_update_inventory(line):
	return line.line_type == "Item" and line.item and line.affects_inventory


def apply_item_movement(item, quantity, rate, transaction_type):
	doc = frappe.get_doc("Item", item)
	qty = flt(quantity)
	if transaction_type == "Sale":
		qty = qty * -1
	elif transaction_type not in ("Purchase", "Sale"):
		return

	if flt(doc.quantity_on_hand) + qty < 0:
		frappe.throw(_("Item {0} does not have enough quantity on hand.").format(doc.item_name or doc.name))

	doc.quantity_on_hand = flt(doc.quantity_on_hand) + qty
	if transaction_type == "Purchase" and flt(rate):
		doc.valuation_rate = flt(rate)
	doc.total_value = flt(doc.quantity_on_hand) * flt(doc.valuation_rate)
	doc.save(ignore_permissions=True)
