import frappe
from frappe.model.document import Document
from frappe.utils import getdate, now


class OwnerTask(Document):
	def validate(self):
		self.set_schedule_defaults()
		self.set_completion_fields()

	def set_schedule_defaults(self):
		if not self.due_date:
			self.due_date = getdate()
		if not self.starts_on:
			self.starts_on = f"{self.due_date} 09:00:00"
		if not self.ends_on:
			self.ends_on = self.starts_on
		if self.ends_on and self.starts_on and self.ends_on < self.starts_on:
			frappe.throw("Ends On cannot be before Starts On.")

	def set_completion_fields(self):
		if self.status == "Completed":
			if not self.completed_on:
				self.completed_on = now()
			if not self.completed_by:
				self.completed_by = frappe.session.user
			self.progress = 100
		elif self.status == "Cancelled":
			self.progress = 0


@frappe.whitelist()
def complete_owner_task(task, completion_notes=None):
	doc = frappe.get_doc("Owner Task", task)
	doc.check_permission("write")
	doc.status = "Completed"
	doc.completion_notes = completion_notes
	doc.completed_on = now()
	doc.completed_by = frappe.session.user
	doc.progress = 100
	doc.save(ignore_permissions=True)
	return {"status": doc.status}
