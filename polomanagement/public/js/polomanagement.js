(function () {
	const KANBAN_UPDATE_METHOD =
		"frappe.desk.doctype.kanban_board.kanban_board.update_order_for_single_card";
	const REPORTVIEW_GET_METHOD = "frappe.desk.reportview.get";

	function is_task_kanban_route() {
		const route = frappe.get_route();
		const route_str = frappe.get_route_str ? frappe.get_route_str() : "";
		const data_route = document.body.getAttribute("data-route") || "";
		const normalized_route = route_str.toLowerCase();
		const normalized_data_route = data_route.toLowerCase();
		const path = window.location.pathname.toLowerCase();

		return (
			(route &&
				String(route[0] || "").toLowerCase() === "list" &&
				String(route[1] || "").toLowerCase() === "task" &&
				String(route[2] || "").toLowerCase() === "kanban") ||
			normalized_route.startsWith("list/task/kanban") ||
			normalized_route.startsWith("task/view/kanban") ||
			normalized_data_route.startsWith("list/task/kanban") ||
			normalized_data_route.startsWith("task/view/kanban") ||
			path.includes("/desk/task/view/kanban")
		);
	}

	function is_limited_groom() {
		return (
			frappe.user.has_role("Horse Groom") &&
			!frappe.user.has_role("Stable Manager") &&
			!frappe.user.has_role("System Manager")
		);
	}

	function update_task_kanban_class() {
		const task_kanban = is_task_kanban_route();
		document.body.classList.toggle("pm-task-kanban", task_kanban);
		document.body.classList.toggle("pm-task-groom", task_kanban && is_limited_groom());

		if (task_kanban) {
			compact_task_kanban();
		}
	}

	function compact_task_kanban() {
		const $kanban = $(".kanban");
		$kanban.find(".add-card, .new-card-area").remove();
		$kanban
			.find(".kanban-assignments, .avatar-action, .avatar-group, .like-action, .list-comment-count")
			.remove();
		$kanban.find(".kanban-card-meta, .kanban-card-doc").remove();

		$kanban.find(".kanban-card:not(.add-card)").css({
			"min-height": "30px",
			"margin-top": "4px",
		});
		$kanban.find(".kanban-card-body").css({
			padding: "6px 10px",
		});
		$kanban.find(".kanban-title-area").css({
			"margin-bottom": "0",
		});
		$kanban.find(".kanban-card-title").css({
			"font-size": "13px",
			"line-height": "18px",
			"display": "-webkit-box",
			"-webkit-line-clamp": "1",
			"-webkit-box-orient": "vertical",
			overflow: "hidden",
		});
	}

	function patch_frappe_call_for_task_kanban() {
		if (frappe._pm_task_kanban_call_patched) {
			return;
		}

		frappe._pm_task_kanban_call_patched = true;
		const original_call = frappe.call;

		frappe.call = function (opts) {
			apply_task_kanban_duration_filter(opts);

			if (!should_prompt_for_completion(opts)) {
				return original_call.apply(this, arguments);
			}

			return prompt_for_kanban_completion(original_call, this, opts);
		};
	}

	function apply_task_kanban_duration_filter(opts) {
		if (
			!opts ||
			typeof opts !== "object" ||
			opts.method !== REPORTVIEW_GET_METHOD ||
			!opts.args ||
			opts.args.doctype !== "Task" ||
			opts.args.view !== "Kanban"
		) {
			return;
		}

		const today = frappe.datetime.get_today();
		const day_start = `${today} 00:00:00`;
		const day_end = `${today} 23:59:59`;
		const filters = (opts.args.filters || []).filter((filter) => {
			const fieldname = filter && filter[1];
			return !["due_date", "starts_on", "ends_on"].includes(fieldname);
		});

		filters.push(["Task", "starts_on", "<=", day_end]);
		filters.push(["Task", "ends_on", ">=", day_start]);
		opts.args.filters = filters;
	}

	function should_prompt_for_completion(opts) {
		return (
			opts &&
			typeof opts === "object" &&
			opts.method === KANBAN_UPDATE_METHOD &&
			opts.args &&
			opts.args.to_colname === "Completed" &&
			!opts.args.completion_notes_prompted
		);
	}

	function prompt_for_kanban_completion(original_call, context, opts) {
		const deferred = $.Deferred();
		let submitted = false;

		frappe.dom.unfreeze();

		const dialog = new frappe.ui.Dialog({
			title: __("Complete Task"),
			fields: [
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
			],
			primary_action_label: __("Complete"),
			primary_action(values) {
				submitted = true;
				dialog.hide();

				const next_opts = {
					...opts,
					args: {
						...opts.args,
						completion_notes: values.completion_notes,
						issue_reported: values.issue_reported,
						completion_notes_prompted: 1,
					},
				};
				const request = original_call.call(context, next_opts);
				request.done((...args) => deferred.resolve(...args));
				request.fail((...args) => deferred.reject(...args));
			},
			secondary_action_label: __("Cancel"),
			secondary_action() {
				dialog.hide();
			},
		});

		dialog.onhide = () => {
			if (!submitted) {
				deferred.reject();
			}
		};
		dialog.show();
		return deferred.promise();
	}

	function show_task_instructions(task_name) {
		frappe.db
			.get_value("Task", task_name, ["subject", "instructions"])
			.then((r) => {
				const doc = r.message || {};
				const title = doc.subject || task_name;
				const instructions = doc.instructions
					? frappe.utils.escape_html(doc.instructions).replace(/\n/g, "<br>")
					: __("No instructions provided.");

				frappe.msgprint({
					title,
					message: instructions,
					indicator: "blue",
				});
			});
	}

	$(document).on("click", "body.pm-task-kanban.pm-task-groom .kanban-card-wrapper a", function (event) {
		event.preventDefault();
		event.stopPropagation();

		const task_name = decodeURIComponent($(this).closest(".kanban-card-wrapper").data("name"));
		if (task_name) {
			show_task_instructions(task_name);
		}
	});

	patch_frappe_call_for_task_kanban();
	$(document).on("page-change", update_task_kanban_class);
	frappe.router.on("change", () => {
		setTimeout(update_task_kanban_class, 0);
		setTimeout(update_task_kanban_class, 300);
		setTimeout(update_task_kanban_class, 1000);
	});

	$(document).on("DOMNodeInserted", ".kanban, .kanban *", () => {
		if (is_task_kanban_route()) {
			compact_task_kanban();
		}
	});

	const observer = new MutationObserver(() => {
		if (is_task_kanban_route()) {
			compact_task_kanban();
		}
	});

	observer.observe(document.body, { childList: true, subtree: true });
	setInterval(() => {
		if (is_task_kanban_route()) {
			compact_task_kanban();
		}
	}, 1000);
})();
