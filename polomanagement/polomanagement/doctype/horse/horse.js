// Copyright (c) 2026, Keenan Solomon and contributors
// For license information, please see license.txt

frappe.ui.form.on("Horse", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		render_owner_dashboard(frm);

		const reports = [
			["Medical Records", "Horse Medical Records", "Horse Medical Record"],
			["Feeding Records", "Horse Feeding Records", "Horse Feeding Record"],
			["Training Records", "Horse Training Records", "Horse Training Record"],
		];

		reports.forEach(([label, _report, doctype]) => {
			frm.add_custom_button(__("New {0}", [label.slice(0, -1)]), () => {
				frappe.new_doc(doctype, { horse: frm.doc.name });
			}, __("Records"));
		});

		frm.add_custom_button(__("New Tack Setup"), () => {
			frappe.new_doc("Horse Tack Configuration", { horse: frm.doc.name });
		}, __("Polo Operations"));

		frm.add_custom_button(__("Compliance Alerts"), () => {
			frappe.route_options = { horse: frm.doc.name };
			frappe.set_route("query-report", "Horse Compliance Alerts");
		}, __("Polo Operations"));
	},

	medical_records_report(frm) {
		open_horse_report(frm, "Horse Medical Records");
	},

	feeding_records_report(frm) {
		open_horse_report(frm, "Horse Feeding Records");
	},

	training_records_report(frm) {
		open_horse_report(frm, "Horse Training Records");
	},
});

function open_horse_report(frm, report_name) {
	frappe.route_options = {
		horse: frm.doc.name,
	};
	frappe.set_route("query-report", report_name);
}

function render_owner_dashboard(frm) {
	const wrapper = frm.fields_dict.owner_dashboard && frm.fields_dict.owner_dashboard.$wrapper;
	if (!wrapper) {
		return;
	}

	wrapper.html(`<div class="pm-horse-dashboard pm-loading">${__("Loading horse dashboard...")}</div>`);
	frappe.call({
		method: "polomanagement.owner_dashboard.get_horse_dashboard",
		args: { horse: frm.doc.name },
		callback(r) {
			const data = r.message || {};
			wrapper.html(get_owner_dashboard_html(frm, data));
			bind_owner_dashboard_actions(frm, wrapper);
		},
	});
}

function get_owner_dashboard_html(frm, data) {
	const summary = data.summary || {};
	const metrics = data.metrics || {};
	const issues = data.issues || [];
	const records = data.records || {};
	const upcoming = data.upcoming || {};
	const money = data.money || {};
	const operations = data.operations || {};
	const money_metrics = money.metrics || {};
	const esc = frappe.utils.escape_html;
	const status = summary.availability_status || "Availability not set";
	const playing = summary.playing_status || "Playing status not set";
	const horse_name = summary.display_name || frm.doc.name1 || frm.doc.name;
	const location_bits = [summary.current_location, summary.stable_number && `Stable ${summary.stable_number}`].filter(Boolean);

	return `
		<div class="pm-horse-dashboard">
			<div class="pm-horse-hero">
				${summary.passport ? `<img class="pm-horse-photo" src="${esc(summary.passport)}" alt="">` : `<div class="pm-horse-photo pm-horse-photo-empty">${esc((horse_name || "?").slice(0, 1))}</div>`}
				<div class="pm-horse-hero-main">
					<div class="pm-horse-kicker">${esc([summary.sex, summary.breed, summary.colour].filter(Boolean).join(" / ") || "Polo horse")}</div>
					<div class="pm-horse-title">${esc(horse_name)}</div>
					<div class="pm-horse-subtitle">${esc(location_bits.join(" / ") || "No location set")}</div>
				</div>
				<div class="pm-horse-status-stack">
					<span class="pm-status-pill">${esc(status)}</span>
					<span class="pm-status-pill pm-status-muted">${esc(playing)}</span>
				</div>
			</div>

			<div class="pm-owner-metrics">
				${metric("Open Tasks", metrics.open_tasks || 0)}
				${metric("Open Issues", metrics.open_issues || 0, metrics.open_issues ? "danger" : "")}
				${metric("Compliance Due", metrics.compliance_due || 0, metrics.compliance_due ? "warning" : "")}
				${metric("Medical 30d", metrics.medical_30d || 0)}
				${metric("Training 30d", metrics.training_30d || 0)}
			</div>

			${summary.special_instructions ? `<div class="pm-owner-note"><strong>${__("Special Instructions")}</strong><span>${esc(summary.special_instructions)}</span></div>` : ""}

			<div class="pm-owner-grid">
				${panel("Issues", issues.length ? issues.map(issue_item).join("") : empty("No open issue history"), "issues")}
				${panel("Upcoming", upcoming_items(upcoming), "upcoming")}
				${panel("Recent Records", recent_records(records), "records")}
				${panel("Polo Operations", operation_rows(operations), "operations")}
			</div>

			<div class="pm-owner-section-title">${__("Money")}</div>
			<div class="pm-owner-metrics">
				${metric("Expenses 30d", format_money(money_metrics.expenses_30d || 0))}
				${metric("Expenses YTD", format_money(money_metrics.expenses_ytd || 0))}
				${metric("Income YTD", format_money(money_metrics.income_ytd || 0))}
				${metric("Unposted", money_metrics.unposted || 0, money_metrics.unposted ? "warning" : "")}
			</div>

			<div class="pm-owner-grid">
				${panel("Recent Transactions", recent_payments(money.payments || []), "payments")}
				${panel("Quotes", quote_rows(money.quotes || []), "quotes")}
				${panel("Unposted Transactions", unposted_rows(money.unposted || []), "unposted")}
			</div>

			<div class="pm-owner-actions">
				<button class="btn btn-xs btn-default" data-pm-action="tasks">${__("Open Tasks")}</button>
				<button class="btn btn-xs btn-default" data-pm-action="issues">${__("Open Issues")}</button>
				<button class="btn btn-xs btn-default" data-pm-action="medical">${__("Medical")}</button>
				<button class="btn btn-xs btn-default" data-pm-action="compliance">${__("Compliance")}</button>
				<button class="btn btn-xs btn-default" data-pm-action="training">${__("Training")}</button>
				<button class="btn btn-xs btn-default" data-pm-action="feeding">${__("Feeding")}</button>
				<button class="btn btn-xs btn-default" data-pm-action="match-days">${__("Match Days")}</button>
				<button class="btn btn-xs btn-default" data-pm-action="travel">${__("Travel")}</button>
				<button class="btn btn-xs btn-default" data-pm-action="tack">${__("Tack")}</button>
				<button class="btn btn-xs btn-default" data-pm-action="horse-expenses">${__("Horse Expenses")}</button>
				<button class="btn btn-xs btn-default" data-pm-action="payments">${__("Transactions")}</button>
				<button class="btn btn-xs btn-default" data-pm-action="quotes">${__("Quotes")}</button>
				<button class="btn btn-xs btn-default" data-pm-action="unposted">${__("Unposted")}</button>
				<button class="btn btn-xs btn-primary" data-pm-action="upload-receipt">${__("Upload Receipt")}</button>
				<button class="btn btn-xs btn-primary" data-pm-action="new-transaction">${__("New Transaction")}</button>
			</div>
		</div>
	`;
}

function metric(label, value, tone) {
	return `<div class="pm-owner-metric ${tone ? `pm-owner-metric-${tone}` : ""}">
		<div class="pm-owner-metric-value">${frappe.utils.escape_html(String(value))}</div>
		<div class="pm-owner-metric-label">${frappe.utils.escape_html(label)}</div>
	</div>`;
}

function panel(title, body, extra_class) {
	return `<section class="pm-owner-panel pm-owner-panel-${extra_class}">
		<header>${frappe.utils.escape_html(title)}</header>
		<div>${body}</div>
	</section>`;
}

function empty(text) {
	return `<div class="pm-owner-empty">${frappe.utils.escape_html(text)}</div>`;
}

function format_money(value) {
	return frappe.format(value || 0, { fieldtype: "Currency" });
}

function issue_item(issue) {
	const esc = frappe.utils.escape_html;
	const priority = issue.issue_priority || "Normal";
	return `<a class="pm-owner-row pm-owner-issue" data-doctype="Task" data-name="${esc(issue.name)}">
		<span class="pm-owner-row-main">${esc(issue.subject || issue.name)}</span>
		<span class="pm-owner-row-meta">${esc(priority)} / ${esc(issue.issue_status || "Open")}</span>
		${issue.completion_notes ? `<span class="pm-owner-row-note">${esc(issue.completion_notes)}</span>` : ""}
	</a>`;
}

function upcoming_items(upcoming) {
	const tasks = (upcoming.tasks || []).map((task) => owner_row("Task", task.name, task.subject, [task.due_date, task.task_type]));
	const owner_tasks = (upcoming.owner_tasks || []).map((task) => owner_row("Owner Task", task.name, task.subject, [task.due_date, task.priority]));
	return tasks.concat(owner_tasks).join("") || empty("Nothing scheduled soon");
}

function recent_records(records) {
	const rows = []
		.concat((records.medical || []).map((row) => owner_row("Horse Medical Record", row.name, row.summary, [row.record_date, row.record_type])))
		.concat((records.training || []).map((row) => owner_row("Horse Training Record", row.name, row.work_type || row.outcome, [row.training_date, row.outcome])))
		.concat((records.feeding || []).map((row) => owner_row("Horse Feeding Record", row.name, row.item, [row.feeding_date, [row.quantity, row.unit].filter(Boolean).join(" ")])));

	return rows.join("") || empty("No recent records");
}

function operation_rows(operations) {
	const rows = []
		.concat((operations.compliance || []).map((row) => owner_row("Horse Medical Record", row.name, row.summary || row.record_type, [row.record_type, row.next_due_date])))
		.concat((operations.matches || []).map((row) => owner_row("Match Day", row.name, row.event_name, [row.match_date, row.venue, row.chukker_number && `Chukker ${row.chukker_number}`, row.status])))
		.concat((operations.travel || []).map((row) => owner_row("Travel Manifest", row.name, row.trip_name, [row.departure_date, row.destination, row.paperwork_status])))
		.concat((operations.tack || []).map((row) => owner_row("Horse Tack Configuration", row.name, row.configuration_name, [row.bit, row.martingale])));

	return rows.join("") || empty("No polo operations planned");
}

function recent_payments(payments) {
	const rows = (payments || []).map((row) => {
		const amount = `${row.direction === "Money In" ? "+" : "-"}${format_money(row.total)}`;
		const title = [row.transaction_category, amount].filter(Boolean).join(" / ");
		return owner_row("Transaction Input", row.name, title, [row.posting_date, row.vendor, row.description]);
	});
	return rows.join("") || empty("No transaction history");
}

function quote_rows(quotes) {
	const rows = (quotes || []).map((row) => {
		const title = [row.quote_title || row.name, format_money(row.total_amount)].filter(Boolean).join(" / ");
		return owner_row("Vendor Quote", row.name, title, [row.status, row.vendor, row.valid_until || row.quote_date]);
	});
	return rows.join("") || empty("No active quotes");
}

function unposted_rows(transactions) {
	const rows = (transactions || []).map((row) => {
		const title = [row.transaction_category || row.transaction_type, format_money(row.total_amount)].filter(Boolean).join(" / ");
		return owner_row("Transaction Input", row.name, title, [row.transaction_date, row.vendor]);
	});
	return rows.join("") || empty("Nothing waiting to post");
}

function owner_row(doctype, name, title, meta_parts) {
	const esc = frappe.utils.escape_html;
	return `<a class="pm-owner-row" data-doctype="${esc(doctype)}" data-name="${esc(name)}">
		<span class="pm-owner-row-main">${esc(title || name)}</span>
		<span class="pm-owner-row-meta">${esc((meta_parts || []).filter(Boolean).join(" / "))}</span>
	</a>`;
}

function bind_owner_dashboard_actions(frm, wrapper) {
	wrapper.find("[data-doctype][data-name]").on("click", function () {
		frappe.set_route("Form", $(this).data("doctype"), $(this).data("name"));
	});

	wrapper.find("[data-pm-action]").on("click", function () {
		const action = $(this).data("pm-action");
		if (action === "tasks") {
			frappe.route_options = { horse: frm.doc.name };
			frappe.set_route("List", "Task", "List");
		} else if (action === "issues") {
			frappe.route_options = { horse: frm.doc.name, issue_status: "Open" };
			frappe.set_route("query-report", "Owner Task Issues");
		} else if (action === "medical") {
			open_horse_report(frm, "Horse Medical Records");
		} else if (action === "compliance") {
			frappe.route_options = { horse: frm.doc.name };
			frappe.set_route("query-report", "Horse Compliance Alerts");
		} else if (action === "training") {
			open_horse_report(frm, "Horse Training Records");
		} else if (action === "feeding") {
			open_horse_report(frm, "Horse Feeding Records");
		} else if (action === "match-days") {
			frappe.route_options = { horse: frm.doc.name };
			frappe.set_route("List", "Match Day", "List");
		} else if (action === "travel") {
			frappe.route_options = { horse: frm.doc.name };
			frappe.set_route("List", "Travel Manifest", "List");
		} else if (action === "tack") {
			frappe.route_options = { horse: frm.doc.name };
			frappe.set_route("List", "Horse Tack Configuration", "List");
		} else if (action === "horse-expenses") {
			open_horse_report(frm, "Horse Expenses");
		} else if (action === "payments") {
			open_horse_report(frm, "Financial Ledger");
		} else if (action === "quotes") {
			frappe.route_options = { linked_horse: frm.doc.name };
			frappe.set_route("query-report", "Quote Comparison");
		} else if (action === "unposted") {
			frappe.route_options = { horse: frm.doc.name };
			frappe.set_route("query-report", "Unposted Transactions");
		} else if (action === "upload-receipt") {
			show_receipt_upload_dialog(frm);
		} else if (action === "new-transaction") {
			frappe.new_doc("Transaction Input");
		}
	});
}

function show_receipt_upload_dialog(frm) {
	if (window.polomanagement_upload_receipts) {
		window.polomanagement_upload_receipts({ linked_horse: frm.doc.name });
	}
}
