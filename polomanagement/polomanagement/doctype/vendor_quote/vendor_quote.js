frappe.ui.form.on("Vendor Quote", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		if (frm.doc.purchase) {
			frm.add_custom_button(__("Open Purchase"), () => {
				frappe.set_route("Form", "Purchase", frm.doc.purchase);
			});
		}

		if (frm.doc.status !== "Selected") {
			frm.add_custom_button(__("Select Quote"), () => {
				frappe.call({
					method: "polomanagement.polomanagement.doctype.vendor_quote.vendor_quote.select_quote",
					args: { quote: frm.doc.name, reject_competing: 1 },
					callback: () => {
						if (frm.doc.purchase) {
							frappe.set_route("Form", "Purchase", frm.doc.purchase);
						} else {
							frm.reload_doc();
						}
					},
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

frappe.ui.form.on("Vendor Quote Line", {
	quantity: calculate_vendor_quote_line,
	rate: calculate_vendor_quote_line,
	tax_amount: calculate_vendor_quote_line,
});

function calculate_vendor_quote_line(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	row.quantity = flt(row.quantity) || 1;
	row.total = row.quantity * (flt(row.rate) || 0) + (flt(row.tax_amount) || 0);
	frm.refresh_field("lines");
	const total = (frm.doc.lines || []).reduce((sum, line) => sum + (flt(line.total) || 0), 0);
	frm.set_value("total_amount", total);
}
