frappe.query_reports["Owner Task Issues"] = {
	filters: [
		{
			fieldname: "issue_status",
			label: __("Issue Status"),
			fieldtype: "Select",
			options: "\nOpen\nAcknowledged\nResolved",
			default: "Open",
		},
		{
			fieldname: "issue_priority",
			label: __("Priority"),
			fieldtype: "Select",
			options: "\nLow\nNormal\nHigh\nUrgent",
		},
		{
			fieldname: "horse",
			label: __("Horse"),
			fieldtype: "Link",
			options: "Horse",
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
		},
	],
};
