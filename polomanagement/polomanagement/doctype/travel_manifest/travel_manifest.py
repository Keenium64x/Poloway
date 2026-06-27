import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class TravelManifest(Document):
	def validate(self):
		if not self.departure_date:
			self.departure_date = getdate()
		self.validate_horses()

	def validate_horses(self):
		seen = set()
		for row in self.horses:
			if row.horse in seen:
				frappe.throw(f"Horse {row.horse} is already on this manifest.")
			seen.add(row.horse)

