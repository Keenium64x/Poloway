import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class MatchDay(Document):
	def validate(self):
		if not self.match_date:
			self.match_date = getdate()
		self.validate_chukkers()

	def validate_chukkers(self):
		seen = set()
		for row in self.chukkers:
			key = (row.chukker_number, row.horse)
			if key in seen:
				frappe.throw(f"Horse {row.horse} is already assigned to chukker {row.chukker_number}.")
			seen.add(key)

