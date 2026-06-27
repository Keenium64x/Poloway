frappe.query_reports["Unposted Transactions"] = {
	filters: [
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nDraft\nSubmitted\nCancelled",
			default: "Draft",
		},
		{
			fieldname: "vendor",
			label: __("Vendor"),
			fieldtype: "Link",
			options: "Vendor",
		},
		{
			fieldname: "horse_owner",
			label: __("Owner"),
			fieldtype: "Link",
			options: "Horse Owner",
		},
		{
			fieldname: "groom_profile",
			label: __("Groom"),
			fieldtype: "Link",
			options: "Groom Profile",
		},
		{
			fieldname: "horse",
			label: __("Horse"),
			fieldtype: "Link",
			options: "Horse",
		},
	],
};
