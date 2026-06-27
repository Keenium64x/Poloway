import frappe
from frappe.model.document import Document


class PaymentLedgerEntry(Document):
	def before_save(self):
		if not self.is_new():
			frappe.throw("Payment ledger entries are immutable. Create a reversal entry instead.")

