frappe.ui.form.on("Task", {
	setup(frm) {
		frm.set_query("feed_item", () => ({
			query: "polomanagement.polomanagement.doctype.item.item.food_item_query",
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

		if (frm.doc.issue_reported && frm.doc.issue_status !== "Resolved") {
			if (frm.doc.issue_status === "Open") {
				frm.add_custom_button(__("Acknowledge Issue"), () => update_issue_status(frm, "acknowledge"), __("Issue"));
			}
			frm.add_custom_button(__("Resolve Issue"), () => update_issue_status(frm, "resolve"), __("Issue"));
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
			{
				fieldname: "issue_priority",
				fieldtype: "Select",
				label: __("Issue Priority"),
				options: "Low\nNormal\nHigh\nUrgent",
				default: frm.doc.issue_priority || "Normal",
				depends_on: "eval:doc.issue_reported",
			},
		],
		(values) => {
			frappe.call({
				method: "polomanagement.polomanagement.doctype.task.task.complete_task",
				args: {
					task: frm.doc.name,
					completion_notes: values.completion_notes,
					issue_reported: values.issue_reported,
					issue_priority: values.issue_priority,
				},
				callback: () => frm.reload_doc(),
			});
		},
		__("Complete Task"),
		__("Complete")
	);
}

function update_issue_status(frm, action) {
	const method =
		action === "resolve"
			? "polomanagement.polomanagement.doctype.task.task.resolve_issue"
			: "polomanagement.polomanagement.doctype.task.task.acknowledge_issue";
	const title = action === "resolve" ? __("Resolve Issue") : __("Acknowledge Issue");
	const primary = action === "resolve" ? __("Resolve") : __("Acknowledge");

	frappe.prompt(
		[
			{
				fieldname: "owner_follow_up",
				fieldtype: "Long Text",
				label: __("Owner Follow Up"),
				default: frm.doc.owner_follow_up,
			},
		],
		(values) => {
			frappe.call({
				method,
				args: {
					task: frm.doc.name,
					owner_follow_up: values.owner_follow_up,
				},
				callback: () => frm.reload_doc(),
			});
		},
		title,
		primary
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
