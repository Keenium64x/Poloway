frappe.ui.form.on("Groom Profile", {
	refresh(frm) {
		if (frm.is_new() || frappe.user.has_role("Horse Groom")) {
			return;
		}

		frm.add_custom_button(__("Create Salary Transaction"), () => {
			const dialog = new frappe.ui.Dialog({
				title: __("Create Salary Transaction"),
				fields: [
					{
						fieldname: "posting_date",
						label: __("Posting Date"),
						fieldtype: "Date",
						default: frappe.datetime.get_today(),
						reqd: 1,
					},
					{
						fieldname: "submit_transaction",
						label: __("Submit Transaction Immediately"),
						fieldtype: "Check",
					},
				],
				primary_action_label: __("Create"),
				primary_action(values) {
					frappe.call({
						method: "polomanagement.payroll.create_salary_transaction",
						args: {
							groom_profile: frm.doc.name,
							posting_date: values.posting_date,
							submit_transaction: values.submit_transaction,
						},
						callback(r) {
							dialog.hide();
							if (r.message?.transaction_input) {
								frappe.set_route("Form", "Transaction Input", r.message.transaction_input);
							}
						},
					});
				},
			});
			dialog.show();
		});
	},

	validate(frm) {
		const parts = [frm.doc.first_name, frm.doc.last_name].filter(Boolean);
		frm.set_value("groom_name", parts.join(" "));
	},
});
