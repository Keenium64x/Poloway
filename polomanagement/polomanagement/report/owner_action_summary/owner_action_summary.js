frappe.query_reports["Owner Action Summary"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_days(frappe.datetime.get_today(), 14),
		},
		{
			fieldname: "source",
			label: __("Source"),
			fieldtype: "Select",
			options: "All\nOwner Task\nGroom Task",
			default: "All",
		},
		{
			fieldname: "horse",
			label: __("Horse"),
			fieldtype: "Link",
			options: "Horse",
		},
	],
};
