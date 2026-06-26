frappe.query_reports["Horse Expenses"] = {
	filters: [
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
		{
			fieldname: "transaction_category",
			label: __("Category"),
			fieldtype: "Select",
			options: "\nFeed\nEquipment\nHorse Purchase\nHorse Sale\nMedical\nFarrier\nTraining\nTournament\nTransport\nService\nOther",
		},
		{
			fieldname: "vendor",
			label: __("Vendor"),
			fieldtype: "Link",
			options: "Vendor",
		},
	],
};
