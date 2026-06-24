import frappe
from frappe.model.document import Document
from frappe.utils import nowtime


class HorseCareEntry(Document):
	def validate(self):
		if self.entry_type == "Feeding":
			self.validate_feeding()

	def on_update(self):
		if self.entry_type in ("Feeding", "Training", "Medical"):
			self.sync_linked_record()

	def validate_feeding(self):
		if not self.feed_item:
			frappe.throw("Feed Item is required for feeding entries.")
		if not self.quantity:
			frappe.throw("Quantity is required for feeding entries.")

		category = frappe.db.get_value("Horse Feed Item", self.feed_item, "category")
		if category != "Food":
			frappe.throw("Feeding entries can only use items in the Food category.")

	def get_record_values(self):
		if self.entry_type == "Feeding":
			return "Horse Feeding Record", {
				"feeding_date": self.entry_date,
				"feeding_time": self.entry_time or nowtime(),
				"horse": self.horse,
				"item": self.feed_item,
				"quantity": self.quantity,
				"unit": self.unit,
				"responsible_person": frappe.session.user,
				"instructions": self.notes,
			}
		elif self.entry_type == "Training":
			return "Horse Training Record", {
				"training_date": self.entry_date,
				"horse": self.horse,
				"training_template": self.training_template,
				"trainer": self.trainer or frappe.session.user,
				"work_type": self.work_type,
				"duration": self.duration,
				"intensity": self.intensity,
				"outcome": "Completed",
				"notes": self.notes,
			}
		elif self.entry_type == "Medical":
			return "Horse Medical Record", {
				"record_date": self.entry_date,
				"horse": self.horse,
				"record_type": self.medical_record_type,
				"status": "Completed",
				"responsible_person": self.responsible_person or frappe.session.user,
				"summary": self.medical_summary or self.notes or self.entry_type,
				"notes": self.notes,
			}

		frappe.throw("Only Feeding, Training, and Medical entries can create records.")

	def sync_linked_record(self):
		doctype, values = self.get_record_values()

		if self.linked_record:
			record = frappe.get_doc(self.linked_record_type, self.linked_record)
			record.update(values)
			record.save(ignore_permissions=True)
			return record.doctype, record.name

		values["doctype"] = doctype
		record = frappe.get_doc(values)
		record.insert(ignore_permissions=True)
		self.db_set({
			"linked_record_type": record.doctype,
			"linked_record": record.name,
		})
		return record.doctype, record.name


@frappe.whitelist()
def create_record(entry):
	doc = frappe.get_doc("Horse Care Entry", entry)
	doc.check_permission("write")
	record_type, record = doc.sync_linked_record()
	return {"linked_record_type": record_type, "linked_record": record}
