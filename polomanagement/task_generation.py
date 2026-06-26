import frappe
from frappe.utils import add_to_date, cint, getdate


def generate_tomorrows_tasks():
	settings = frappe.get_single("Task Schedule Settings")
	if not settings.enabled:
		return []

	days_ahead = cint(settings.days_ahead) or 1
	target_date = add_to_date(getdate(), days=days_ahead)
	return generate_tasks_for_date(target_date)


@frappe.whitelist()
def generate_tasks_for_date(schedule_date=None):
	settings = frappe.get_single("Task Schedule Settings")
	schedule_date = getdate(schedule_date) if schedule_date else add_to_date(getdate(), days=1)
	template_name = get_template_for_date(settings, schedule_date)
	if not template_name:
		frappe.throw("Choose a default template or add a template override for this date first.")

	template = frappe.get_doc("Task Template", template_name)
	if not template.is_active:
		frappe.throw(f"Template {template.template_name or template.name} is not active.")
	if not template.items:
		frappe.throw(f"Template {template.template_name or template.name} has no task items.")

	created = []
	for item in template.items:
		task = create_task_from_template_item(settings, template, item, schedule_date)
		if task:
			created.append(task.name)

	settings.db_set("last_generated_for", schedule_date)
	return created


def get_template_for_date(settings, schedule_date):
	for override in settings.overrides:
		if getdate(override.schedule_date) == schedule_date:
			return override.template
	return settings.default_template


def create_task_from_template_item(settings, template, item, schedule_date):
	generation_key = f"{schedule_date}:{template.name}:{item.name}"
	existing = frappe.db.get_value("Task", {"template_generation_key": generation_key}, "name")
	if existing:
		return None

	starts_on = combine_date_time(schedule_date, item.starts_at, "08:00:00")
	ends_on = combine_date_time(schedule_date, item.ends_at or item.starts_at, "08:00:00")
	if item.all_day:
		starts_on = f"{schedule_date} 00:00:00"
		ends_on = f"{schedule_date} 23:59:59"

	task = frappe.get_doc({
		"doctype": "Task",
		"subject": item.subject,
		"status": "Open",
		"task_type": item.task_type,
		"assigned_to": item.assigned_to or settings.default_assigned_to,
		"horse": item.horse,
		"owner_visible": 1,
		"due_date": schedule_date,
		"starts_on": starts_on,
		"ends_on": ends_on,
		"all_day": item.all_day,
		"instructions": item.instructions,
		"feed_item": item.feed_item,
		"quantity": item.quantity,
		"unit": item.unit,
		"feeding_time": item.feeding_time or item.starts_at,
		"training_template": item.training_template,
		"trainer": item.trainer or item.assigned_to or settings.default_assigned_to,
		"work_type": item.work_type,
		"duration": item.duration,
		"intensity": item.intensity,
		"medical_record_type": item.medical_record_type,
		"responsible_person": item.responsible_person or item.assigned_to or settings.default_assigned_to,
		"medical_summary": item.medical_summary,
		"generated_from_template": template.name,
		"generated_from_template_item": item.name,
		"template_generation_key": generation_key,
	})
	task.insert(ignore_permissions=True)
	return task


def combine_date_time(date_value, time_value, default_time):
	if not time_value:
		time_value = default_time

	time_text = str(time_value)
	if len(time_text) == 5:
		time_text = f"{time_text}:00"

	return f"{date_value} {time_text}"
