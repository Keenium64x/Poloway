frappe.ui.form.on("Payment Record", {
	refresh(frm) {
		if (frm.doc.source_transaction) {
			frm.add_custom_button(__("Open Transaction"), () => {
				frappe.set_route("Form", "Transaction Input", frm.doc.source_transaction);
			});
		}

		if (frm.doc.selected_quote) {
			frm.add_custom_button(__("Open Quote"), () => {
				frappe.set_route("Form", "Vendor Quote", frm.doc.selected_quote);
			});
		}
	},
});
