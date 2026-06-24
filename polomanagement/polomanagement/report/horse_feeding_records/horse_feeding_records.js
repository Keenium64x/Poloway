frappe.query_reports["Horse Feeding Records"] = {
	filters: [
		{
			fieldname: "horse",
			label: __("Horse"),
			fieldtype: "Link",
			options: "Horse",
		},
	],
};
