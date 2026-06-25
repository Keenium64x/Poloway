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

		const limited_groom_view = is_limited_groom_view();
		apply_groom_task_view(frm, limited_groom_view);

		if (frm.doc.status !== "Completed") {
			frm.add_custom_button(__("Complete"), () => complete_task(frm), __("Actions"));
		}

		if (limited_groom_view) {
			return;
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

function is_limited_groom_view() {
	return (
		frappe.user.has_role("Horse Groom") &&
		!frappe.user.has_role("Stable Manager") &&
		!frappe.user.has_role("System Manager")
	);
}

function apply_groom_task_view(frm, limited_groom_view) {
	frm.set_df_property("instructions", "read_only", 1);

	if (!limited_groom_view) {
		return;
	}

	const visible_fields = new Set([
		"instructions_section",
		"instructions",
		"notes_section",
		"completion_notes",
		"issue_reported",
	]);

	frm.meta.fields.forEach((df) => {
		if (!df.fieldname) {
			return;
		}

		const show_field = visible_fields.has(df.fieldname);
		frm.toggle_display(df.fieldname, show_field);

		if (show_field) {
			frm.set_df_property(df.fieldname, "read_only", df.fieldname !== "completion_notes" && df.fieldname !== "issue_reported");
		}
	});

	frm.set_df_property("completion_notes", "depends_on", "");
	frm.set_df_property("issue_reported", "depends_on", "");
	frm.set_df_property("completion_notes", "hidden", 0);
	frm.set_df_property("issue_reported", "hidden", 0);
	frm.toggle_display("completion_notes", true);
	frm.toggle_display("issue_reported", true);
	frm.refresh_fields(["instructions", "completion_notes", "issue_reported"]);
}
