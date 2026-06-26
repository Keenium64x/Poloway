frappe.ui.form.on("Purchase", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		frm.add_custom_button(__("Add Quote"), () => {
			const dialog = new frappe.ui.Dialog({
				title: __("Add Vendor Quote"),
				fields: [
					{
						fieldname: "vendor",
						fieldtype: "Link",
						label: __("Vendor"),
						options: "Vendor",
						reqd: 1,
					},
				],
				primary_action_label: __("Create Quote"),
				primary_action(values) {
					frappe.call({
						method: "polomanagement.polomanagement.doctype.purchase.purchase.create_vendor_quote",
						args: {
							purchase: frm.doc.name,
							vendor: values.vendor,
						},
						freeze: true,
						freeze_message: __("Creating quote..."),
						callback(r) {
							dialog.hide();
							if (r.message) {
								frappe.set_route("Form", "Vendor Quote", r.message);
							}
						},
					});
				},
			});
			dialog.show();
		}, __("Quotes"));

		if (frm.doc.selected_quote && !frm.doc.transaction_input) {
			frm.add_custom_button(__("Create Transaction"), () => {
				create_purchase_transaction(frm, 0);
			}, __("Payment"));
			frm.add_custom_button(__("Post Payment"), () => {
				create_purchase_transaction(frm, 1);
			}, __("Payment"));
		}

		if (frm.doc.transaction_input) {
			frm.add_custom_button(__("Open Transaction"), () => {
				frappe.set_route("Form", "Transaction Input", frm.doc.transaction_input);
			}, __("Payment"));
		}

		if (frm.doc.payment_record) {
			frm.add_custom_button(__("Open Payment"), () => {
				frappe.set_route("Form", "Payment Record", frm.doc.payment_record);
			}, __("Payment"));
		}
	},
});

frappe.ui.form.on("Purchase Line", {
	quantity: calculate_purchase_line,
	rate: calculate_purchase_line,
	tax_amount: calculate_purchase_line,
});

function calculate_purchase_line(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	row.quantity = flt(row.quantity) || 1;
	row.total = row.quantity * (flt(row.rate) || 0) + (flt(row.tax_amount) || 0);
	frm.refresh_field("lines");
	const total = (frm.doc.lines || []).reduce((sum, line) => sum + (flt(line.total) || 0), 0);
	frm.set_value("estimated_total", total);
}

function create_purchase_transaction(frm, post_payment) {
	frappe.call({
		method: "polomanagement.polomanagement.doctype.purchase.purchase.create_transaction_from_selected_quote",
		args: {
			purchase: frm.doc.name,
			post_payment,
		},
		freeze: true,
		freeze_message: __("Creating transaction..."),
		callback(r) {
			const result = r.message || {};
			if (result.payment_record) {
				frappe.set_route("Form", "Payment Record", result.payment_record);
			} else if (result.transaction_input) {
				frappe.set_route("Form", "Transaction Input", result.transaction_input);
			}
		},
	});
}
