frappe.ui.form.on("Task", {
	setup(frm) {
		frm.set_query("feed_item", () => ({
			filters: {
				category: "Food",
				is_active: 1,
			},
		}));
	},

	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		if (frm.doc.status !== "Completed") {
			frm.add_custom_button(__("Complete"), () => complete_task(frm), __("Actions"));
		}

		frm.add_custom_button(__("Open Entry"), () => {
			if (frm.doc.care_entry) {
				frappe.set_route("Form", "Horse Care Entry", frm.doc.care_entry);
			} else {
				frappe.call({
					method: "polomanagement.polomanagement.doctype.task.task.create_care_entry",
					args: { task: frm.doc.name },
					callback: (r) => {
						if (r.message) {
							frm.reload_doc();
							frappe.set_route("Form", "Horse Care Entry", r.message);
						}
					},
				});
			}
		}, __("Actions"));

		if (frm.doc.linked_record_type && frm.doc.linked_record) {
			frm.add_custom_button(__("Open Record"), () => {
				frappe.set_route("Form", frm.doc.linked_record_type, frm.doc.linked_record);
			}, __("Actions"));
		}
	},
});

function complete_task(frm) {
	frappe.prompt(
		[
			{
				fieldname: "completion_notes",
				fieldtype: "Long Text",
				label: __("Completion Notes"),
				default: frm.doc.completion_notes,
			},
			{
				fieldname: "issue_reported",
				fieldtype: "Check",
				label: __("Issue Reported"),
				default: frm.doc.issue_reported,
			},
		],
		(values) => {
			frappe.call({
				method: "polomanagement.polomanagement.doctype.task.task.complete_task",
				args: {
					task: frm.doc.name,
					completion_notes: values.completion_notes,
					issue_reported: values.issue_reported,
				},
				callback: () => frm.reload_doc(),
			});
		},
		__("Complete Task"),
		__("Complete")
	);
}
