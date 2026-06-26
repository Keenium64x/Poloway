import frappe
from frappe.model.document import Document


class TaskScheduleSettings(Document):
	def validate(self):
		self.validate_overrides()

	def validate_overrides(self):
		seen = set()
		for override in self.overrides:
			if override.schedule_date in seen:
				frappe.throw(f"Only one template override is allowed for {override.schedule_date}.")
			seen.add(override.schedule_date)

