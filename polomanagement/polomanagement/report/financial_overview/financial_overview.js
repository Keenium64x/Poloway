frappe.query_reports["Financial Overview"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: `${frappe.datetime.get_today().slice(0, 4)}-01-01`,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "horse",
			label: __("Horse"),
			fieldtype: "Link",
			options: "Horse",
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
