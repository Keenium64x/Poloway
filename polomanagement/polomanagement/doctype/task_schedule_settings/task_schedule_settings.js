frappe.ui.form.on("Task Schedule Settings", {
	refresh(frm) {
		frm.add_custom_button(__("Generate Tomorrow"), () => {
			generate_tasks_for_date(frm);
		});

		frm.add_custom_button(__("Generate for Date"), () => {
			frappe.prompt(
				[
					{
						fieldname: "schedule_date",
						fieldtype: "Date",
						label: __("Date"),
						reqd: 1,
						default: frappe.datetime.add_days(frappe.datetime.get_today(), 1),
					},
				],
				(values) => generate_tasks_for_date(frm, values.schedule_date),
				__("Generate Tasks"),
				__("Generate")
			);
		});
	},
});

function generate_tasks_for_date(frm, schedule_date) {
	frm.save().then(() => {
		frappe.call({
			method: "polomanagement.task_generation.generate_tasks_for_date",
			args: { schedule_date },
			freeze: true,
			freeze_message: __("Generating Tasks"),
			callback(r) {
				const count = (r.message || []).length;
				frappe.show_alert({
					indicator: count ? "green" : "orange",
					message: count
						? __("{0} task(s) generated", [count])
						: __("No new tasks generated. They may already exist for that date."),
				});
				frm.reload_doc();
			},
		});
	});
}
