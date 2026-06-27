frappe.ui.form.on("Transaction Input", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		if (frm.doc.selected_quote && frm.doc.docstatus === 0) {
			frm.add_custom_button(__("Pull Quote Details"), () => {
				frappe.call({
					method: "polomanagement.polomanagement.doctype.transaction_input.transaction_input.pull_quote_lines",
					args: { transaction_input: frm.doc.name },
					callback: () => frm.reload_doc(),
				});
			});
		}

		if (frm.doc.docstatus === 0) {
			frm.add_custom_button(__("Submit Transaction"), () => {
				frappe.call({
					method: "polomanagement.polomanagement.doctype.transaction_input.transaction_input.submit_transaction",
					args: { transaction_input: frm.doc.name },
					callback: () => frm.reload_doc(),
				});
			}).addClass("btn-primary");
		}

		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__("Financial Ledger"), () => {
				frappe.route_options = { transaction_input: frm.doc.name };
				frappe.set_route("query-report", "Financial Ledger");
			});
		}
	},
});

frappe.ui.form.on("Transaction Input Line", {
	quantity: calculate_transaction_line,
	rate: calculate_transaction_line,
	tax_amount: calculate_transaction_line,
});

function calculate_transaction_line(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	row.quantity = flt(row.quantity) || 1;
	row.total = row.quantity * (flt(row.rate) || 0) + (flt(row.tax_amount) || 0);
	frm.refresh_field("lines");
	const total = (frm.doc.lines || []).reduce((sum, line) => sum + (flt(line.total) || 0), 0);
	frm.set_value("total_amount", total);
}
