frappe.query_reports["Inventory Vendor Summary"] = {
	filters: [
		{
			fieldname: "group_by",
			label: __("Group By"),
			fieldtype: "Select",
			options: "Category\nLocation\nResponsible Role",
			default: "Category",
		},
		{
			fieldname: "item_category",
			label: __("Item Category"),
			fieldtype: "Link",
			options: "Item Category",
		},
		{
			fieldname: "inventory_location",
			label: __("Inventory Location"),
			fieldtype: "Link",
			options: "Inventory Location",
		},
		{
			fieldname: "active_only",
			label: __("Active Only"),
			fieldtype: "Check",
			default: 1,
		},
	],
};
