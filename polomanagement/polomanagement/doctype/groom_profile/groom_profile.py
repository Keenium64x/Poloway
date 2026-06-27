import frappe
from frappe.model.document import Document


class GroomProfile(Document):
	def validate(self):
		self.groom_name = " ".join(part for part in [self.first_name, self.last_name] if part)
		if self.user:
			self.email = self.email or frappe.db.get_value("User", self.user, "email")
