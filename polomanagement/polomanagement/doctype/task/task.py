import frappe
from frappe.model.document import Document
from frappe.utils import cint, getdate, now, nowtime


class Task(Document):
	def validate(self):
		self.set_schedule_defaults()

	def set_schedule_defaults(self):
		if not self.due_date:
			self.due_date = getdate()
		if not self.starts_on:
			self.starts_on = f"{self.due_date} 08:00:00"
		if not self.ends_on:
			self.ends_on = self.starts_on

	def complete(self, completion_notes=None, issue_reported=None):
		if completion_notes is not None:
			self.completion_notes = completion_notes
		if issue_reported is not None:
			self.issue_reported = 1 if cint(issue_reported) else 0

		if self.task_type in ("Feeding", "Training", "Medical"):
			entry = self.get_or_create_care_entry()
			record_type, record = entry.sync_linked_record()
			self.linked_record_type = record_type
			self.linked_record = record

		self.status = "Completed"
		self.progress = 100
		self.completed_on = now()
		self.completed_by = frappe.session.user
		self.save(ignore_permissions=True)
		return self

	def get_or_create_care_entry(self):
		if self.care_entry:
			return frappe.get_doc("Horse Care Entry", self.care_entry)

		if not self.horse:
			frappe.throw("Horse is required before creating a care entry.")

		entry_type = self.task_type
		entry = frappe.get_doc({
			"doctype": "Horse Care Entry",
			"entry_type": entry_type,
			"horse": self.horse,
			"task": self.name,
			"entry_date": self.due_date or getdate(),
			"entry_time": self.feeding_time or nowtime(),
			"feed_item": self.feed_item,
			"quantity": self.quantity,
			"unit": self.unit,
			"training_template": self.training_template,
			"trainer": self.trainer or self.assigned_to,
			"work_type": self.work_type,
			"duration": self.duration,
			"intensity": self.intensity,
			"medical_record_type": self.medical_record_type,
			"responsible_person": self.responsible_person or self.assigned_to,
			"medical_summary": self.medical_summary,
			"notes": self.completion_notes or self.instructions,
		})
		entry.insert(ignore_permissions=True)
		self.db_set("care_entry", entry.name)
		return entry


@frappe.whitelist()
def complete_task(task, completion_notes=None, issue_reported=0):
	doc = frappe.get_doc("Task", task)
	doc.check_permission("write")
	doc.complete(completion_notes=completion_notes, issue_reported=issue_reported)
	return {"status": doc.status, "linked_record_type": doc.linked_record_type, "linked_record": doc.linked_record}


@frappe.whitelist()
def create_care_entry(task):
	doc = frappe.get_doc("Task", task)
	doc.check_permission("write")
	entry = doc.get_or_create_care_entry()
	return entry.name
