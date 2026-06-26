frappe.query_reports["Quote Comparison"] = {
	filters: [
		{
			fieldname: "vendor",
			label: __("Vendor"),
			fieldtype: "Link",
			options: "Vendor",
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nDraft\nSubmitted\nSelected\nRejected\nExpired",
		},
		{
			fieldname: "linked_horse",
			label: __("Horse"),
			fieldtype: "Link",
			options: "Horse",
		},
		{
			fieldname: "tournament",
			label: __("Tournament / Event"),
			fieldtype: "Data",
		},
	],
};
