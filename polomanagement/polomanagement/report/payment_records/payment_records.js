frappe.query_reports["Payment Records"] = {
	filters: [
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
			fieldname: "direction",
			label: __("Direction"),
			fieldtype: "Select",
			options: "\nMoney In\nMoney Out",
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
		{
			fieldname: "horse",
			label: __("Horse"),
			fieldtype: "Link",
			options: "Horse",
		},
	],
};
