import frappe


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = [
		{"label": "Record", "fieldname": "name", "fieldtype": "Link", "options": "Horse Training Record", "width": 160},
		{"label": "Date", "fieldname": "training_date", "fieldtype": "Date", "width": 110},
		{"label": "Horse", "fieldname": "horse", "fieldtype": "Link", "options": "Horse", "width": 160},
		{"label": "Template", "fieldname": "training_template", "fieldtype": "Link", "options": "Horse Training Template", "width": 180},
		{"label": "Trainer", "fieldname": "trainer", "fieldtype": "Link", "options": "User", "width": 180},
		{"label": "Work Type", "fieldname": "work_type", "fieldtype": "Data", "width": 140},
		{"label": "Duration", "fieldname": "duration", "fieldtype": "Duration", "width": 110},
		{"label": "Intensity", "fieldname": "intensity", "fieldtype": "Data", "width": 110},
		{"label": "Outcome", "fieldname": "outcome", "fieldtype": "Data", "width": 140},
		{"label": "Speed", "fieldname": "speed_rating", "fieldtype": "Data", "width": 100},
		{"label": "Responsiveness", "fieldname": "responsiveness_rating", "fieldtype": "Data", "width": 130},
		{"label": "Mouth", "fieldname": "mouth_sensitivity", "fieldtype": "Data", "width": 110},
		{"label": "Notes", "fieldname": "notes", "fieldtype": "Data", "width": 260},
	]
	return columns, get_data(filters)


def get_data(filters):
	conditions = {}
	if filters.horse:
		conditions["horse"] = filters.horse

	return frappe.get_all(
		"Horse Training Record",
		filters=conditions,
		fields=["name", "training_date", "horse", "training_template", "trainer", "work_type", "duration", "intensity", "outcome", "speed_rating", "responsiveness_rating", "mouth_sensitivity", "notes"],
		order_by="training_date desc, creation desc",
	)
