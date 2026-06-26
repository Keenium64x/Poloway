frappe.listview_settings["Task"] = {
	add_fields: [
		"status",
		"due_date",
		"assigned_to",
		"task_type",
		"starts_on",
		"subject",
		"completion_notes",
		"issue_reported",
		"issue_priority",
		"issue_status",
	],
	filters: [
		["due_date", "=", frappe.datetime.get_today()],
		["status", "=", "Open"],
	],
	formatters: {
		completion_notes(value, _df, doc) {
			if (doc.status !== "Completed") {
				return "";
			}

			const note = value ? frappe.utils.escape_html(value) : __("No notes");
			const indicator = doc.issue_reported ? "red" : "green";
			const label = doc.issue_reported ? __("Issue") : __("Done");
			return `<span class="indicator-pill ${indicator}" title="${note}">
				<span class="ellipsis">${label}: ${note}</span>
			</span>`;
		},
	},

	onload(listview) {
		if (
			frappe.user.has_role("Horse Groom") &&
			!frappe.user.has_role("Stable Manager") &&
			!frappe.user.has_role("System Manager")
		) {
			listview.filter_area.add("Task", "assigned_to", "=", frappe.session.user);
		}
	},

	refresh(listview) {
		move_complete_buttons_left(listview);
	},

	button: {
		show(doc) {
			return doc.status === "Open";
		},
		get_label() {
			return __("Complete");
		},
		get_description(doc) {
			return __("Complete {0}", [doc.subject || doc.name]);
		},
		action(doc) {
			frappe.prompt(
				[
					{
						fieldname: "completion_notes",
						fieldtype: "Long Text",
						label: __("Completion Notes"),
					},
					{
						fieldname: "issue_reported",
						fieldtype: "Check",
						label: __("Issue Reported"),
					},
					{
						fieldname: "issue_priority",
						fieldtype: "Select",
						label: __("Issue Priority"),
						options: "Low\nNormal\nHigh\nUrgent",
						default: "Normal",
						depends_on: "eval:doc.issue_reported",
					},
				],
				(values) => {
					frappe.call({
						method: "polomanagement.polomanagement.doctype.task.task.complete_task",
						args: {
							task: doc.name,
							completion_notes: values.completion_notes,
							issue_reported: values.issue_reported,
							issue_priority: values.issue_priority,
						},
						callback: () => cur_list && cur_list.refresh(),
					});
				},
				__("Complete Task"),
				__("Complete")
			);
		},
	},
};

function move_complete_buttons_left(listview) {
	listview.$result.find(".list-row-container .level-left").each(function () {
		const $row = $(this);
		const $button_col = $row.find(".btn-action").closest(".list-row-col");
		if ($button_col.length) {
			$button_col.addClass("task-complete-col").prependTo($row);
		}
	});
}
