frappe.query_reports["Financial Ledger"] = {
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
			fieldname: "account",
			label: __("Account"),
			fieldtype: "Link",
			options: "Money Account",
		},
		{
			fieldname: "transaction_input",
			label: __("Transaction"),
			fieldtype: "Link",
			options: "Transaction Input",
		},
		{
			fieldname: "transaction_category",
			label: __("Category"),
			fieldtype: "Select",
			options: "\nFeed\nEquipment\nSupplies\nSupplements\nGroom Salary\nOvertime Pay\nBenefits\nHorse Purchase\nHorse Sale\nMedical\nFarrier\nTraining\nTournament\nTransport\nService\nOther",
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
		{
			fieldname: "item",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item",
		},
	],
};
