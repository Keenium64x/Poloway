frappe.query_reports["Money Flow Summary"] = {
	filters: [
		{
			fieldname: "period",
			label: __("Period"),
			fieldtype: "Select",
			options: "Monthly\nWeekly\nDaily",
			default: "Monthly",
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -12),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "transaction_category",
			label: __("Category"),
			fieldtype: "Select",
			options: "\nFeed\nEquipment\nSupplies\nSupplements\nGroom Salary\nOvertime Pay\nBenefits\nHorse Purchase\nHorse Sale\nMedical\nFarrier\nTraining\nTournament\nTransport\nService\nOther",
		},
		{
			fieldname: "horse",
			label: __("Horse"),
			fieldtype: "Link",
			options: "Horse",
		},
		{
			fieldname: "vendor",
			label: __("Vendor"),
			fieldtype: "Link",
			options: "Vendor",
		},
	],
};
