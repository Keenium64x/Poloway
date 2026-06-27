frappe.query_reports["Item Stock Ledger"] = {
	filters: [
		{
			fieldname: "item",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item",
		},
		{
			fieldname: "inventory_location",
			label: __("Location"),
			fieldtype: "Link",
			options: "Inventory Location",
		},
		{
			fieldname: "movement_type",
			label: __("Movement"),
			fieldtype: "Select",
			options: "\nPurchase Receipt\nSale Issue\nStock Adjustment\nReversal",
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
	],
};

