frappe.ui.form.on("Owner Task", {
	refresh(frm) {
		if (frm.is_new() || frm.doc.status === "Completed") {
			return;
		}

		frm.add_custom_button(__("Complete"), () => {
			frappe.prompt(
				[
					{
						fieldname: "completion_notes",
						fieldtype: "Long Text",
						label: __("Completion Notes"),
					},
				],
				(values) => {
					frappe.call({
						method: "polomanagement.polomanagement.doctype.owner_task.owner_task.complete_owner_task",
						args: {
							task: frm.doc.name,
							completion_notes: values.completion_notes,
						},
						callback: () => frm.reload_doc(),
					});
				},
				__("Complete Owner Task"),
				__("Complete")
			);
		});
	},
});
