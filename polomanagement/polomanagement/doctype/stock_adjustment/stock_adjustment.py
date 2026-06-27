import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class StockAdjustment(Document):
	def validate(self):
		if not self.posting_date:
			self.posting_date = getdate()
		if not self.lines:
			frappe.throw(_("Add at least one stock adjustment line."))

	def before_submit(self):
		self.status = "Submitted"

	def on_submit(self):
		from polomanagement.polomanagement.stock_ledger import create_item_stock_ledger_entry

		for line in self.lines:
			create_item_stock_ledger_entry(
				item=line.item,
				quantity_change=line.quantity_change,
				valuation_rate=line.valuation_rate,
				movement_type="Stock Adjustment",
				voucher_type=self.doctype,
				voucher_no=self.name,
				voucher_detail_no=line.name,
				posting_date=self.posting_date,
				inventory_location=line.inventory_location,
				remarks=line.remarks or self.reason,
			)

	def on_cancel(self):
		from polomanagement.polomanagement.stock_ledger import reverse_stock_ledger_entries

		reverse_stock_ledger_entries(self.doctype, self.name, self.posting_date)
		self.db_set("status", "Cancelled")

