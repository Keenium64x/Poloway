frappe.ui.form.on("Item", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		frm.add_custom_button(__("Stock Ledger"), () => {
			frappe.route_options = { item: frm.doc.name };
			frappe.set_route("query-report", "Item Stock Ledger");
		});

		frm.add_custom_button(__("Stock Adjustment"), () => {
			frappe.new_doc("Stock Adjustment");
		});
	},
});
