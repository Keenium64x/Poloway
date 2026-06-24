frappe.query_reports["Horse Medical Records"] = {
	filters: [
		{
			fieldname: "horse",
			label: __("Horse"),
			fieldtype: "Link",
			options: "Horse",
		},
	],
};
