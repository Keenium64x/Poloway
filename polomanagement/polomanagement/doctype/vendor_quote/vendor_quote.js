frappe.ui.form.on("Vendor Quote", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		if (frm.doc.status !== "Selected") {
			frm.add_custom_button(__("Select Quote"), () => {
				frappe.call({
					method: "polomanagement.polomanagement.doctype.vendor_quote.vendor_quote.select_quote",
					args: { quote: frm.doc.name, reject_competing: 1 },
					callback: () => frm.reload_doc(),
				});
			});
		}

		frm.add_custom_button(__("Create Transaction"), () => {
			frappe.call({
				method: "polomanagement.polomanagement.doctype.vendor_quote.vendor_quote.create_transaction_input",
				args: { quote: frm.doc.name },
				callback: (r) => {
					if (r.message) {
						frappe.set_route("Form", "Transaction Input", r.message);
					}
				},
			});
		});
	},
});
