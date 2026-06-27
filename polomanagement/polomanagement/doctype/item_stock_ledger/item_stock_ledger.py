import frappe
from frappe.model.document import Document


class ItemStockLedger(Document):
	def before_save(self):
		if not self.is_new():
			frappe.throw("Stock ledger entries are immutable. Create a reversal entry instead.")

