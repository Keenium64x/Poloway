import frappe
from frappe.model.document import Document
from frappe.utils import cint, getdate, now, nowtime
from polomanagement.polomanagement.doctype.item.item import validate_food_item


class Task(Document):
	def validate(self):
		self.set_schedule_defaults()
		self.set_issue_defaults()
		self.validate_feeding_item()

	def validate_feeding_item(self):
		if self.task_type == "Feeding":
			validate_food_item(self.feed_item)

	def set_schedule_defaults(self):
		if not self.due_date:
			self.due_date = getdate()
		if not self.starts_on:
			self.starts_on = f"{self.due_date} 08:00:00"
		if not self.ends_on:
			self.ends_on = self.starts_on

	def set_issue_defaults(self):
		if self.issue_reported:
			if not self.issue_priority:
				self.issue_priority = "Normal"
			if not self.issue_status:
				self.issue_status = "Open"
		else:
			self.issue_status = None
			self.issue_priority = None
			self.owner_follow_up = None
			self.issue_acknowledged_on = None
			self.issue_resolved_on = None

	def complete(self, completion_notes=None, issue_reported=None, issue_priority=None):
		if completion_notes is not None:
			self.completion_notes = completion_notes
		if issue_reported is not None:
			self.issue_reported = 1 if cint(issue_reported) else 0
		if issue_priority:
			self.issue_priority = issue_priority
		if self.issue_reported:
			self.issue_status = self.issue_status or "Open"
			self.issue_priority = self.issue_priority or "Normal"

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

	def acknowledge_issue(self, owner_follow_up=None):
		self.ensure_issue()
		self.issue_status = "Acknowledged"
		self.issue_acknowledged_on = now()
		if owner_follow_up is not None:
			self.owner_follow_up = owner_follow_up
		self.save(ignore_permissions=True)
		return self

	def resolve_issue(self, owner_follow_up=None):
		self.ensure_issue()
		self.issue_status = "Resolved"
		self.issue_resolved_on = now()
		if not self.issue_acknowledged_on:
			self.issue_acknowledged_on = now()
		if owner_follow_up is not None:
			self.owner_follow_up = owner_follow_up
		self.save(ignore_permissions=True)
		return self

	def ensure_issue(self):
		if not self.issue_reported:
			frappe.throw("This task does not have a reported issue.")

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
def complete_task(task, completion_notes=None, issue_reported=0, issue_priority=None):
	doc = frappe.get_doc("Task", task)
	doc.check_permission("write")
	doc.complete(completion_notes=completion_notes, issue_reported=issue_reported, issue_priority=issue_priority)
	return {"status": doc.status, "linked_record_type": doc.linked_record_type, "linked_record": doc.linked_record}


@frappe.whitelist()
def create_care_entry(task):
	doc = frappe.get_doc("Task", task)
	doc.check_permission("write")
	entry = doc.get_or_create_care_entry()
	return entry.name


@frappe.whitelist()
def acknowledge_issue(task, owner_follow_up=None):
	doc = frappe.get_doc("Task", task)
	doc.check_permission("write")
	doc.acknowledge_issue(owner_follow_up=owner_follow_up)
	return {"issue_status": doc.issue_status}


@frappe.whitelist()
def resolve_issue(task, owner_follow_up=None):
	doc = frappe.get_doc("Task", task)
	doc.check_permission("write")
	doc.resolve_issue(owner_follow_up=owner_follow_up)
	return {"issue_status": doc.issue_status}
