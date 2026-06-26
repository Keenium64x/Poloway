frappe.ui.form.on("Transaction Input", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		if (frm.doc.selected_quote && frm.doc.status !== "Posted") {
			frm.add_custom_button(__("Pull Quote Lines"), () => {
				frappe.call({
					method: "polomanagement.polomanagement.doctype.transaction_input.transaction_input.pull_quote_lines",
					args: { transaction_input: frm.doc.name },
					callback: () => frm.reload_doc(),
				});
			});
		}

		if (frm.doc.payment_record) {
			frm.add_custom_button(__("Open Payment Record"), () => {
				frappe.set_route("Form", "Payment Record", frm.doc.payment_record);
			});
			return;
		}

		if (frm.doc.status !== "Cancelled") {
			frm.add_custom_button(__("Create Payment Record"), () => {
				frappe.call({
					method: "polomanagement.polomanagement.doctype.transaction_input.transaction_input.create_payment_record",
					args: { transaction_input: frm.doc.name },
					callback: (r) => {
						if (r.message) {
							frappe.set_route("Form", "Payment Record", r.message);
						}
					},
				});
			}).addClass("btn-primary");
		}
	},
});
