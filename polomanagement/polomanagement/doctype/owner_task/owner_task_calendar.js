frappe.views.calendar["Owner Task"] = {
	field_map: {
		start: "starts_on",
		end: "ends_on",
		id: "name",
		title: "subject",
		allDay: "all_day",
		status: "status",
		progress: "progress",
	},
	gantt: true,
	get_events_method: "frappe.desk.calendar.get_events",
};
