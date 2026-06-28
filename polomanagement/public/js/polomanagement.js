(function () {
	const KANBAN_UPDATE_METHOD =
		"frappe.desk.doctype.kanban_board.kanban_board.update_order_for_single_card";
	const REPORTVIEW_GET_METHOD = "frappe.desk.reportview.get";
	const WORKSPACE_ONBOARDINGS = {
		Poloway: "Poloway System Onboarding",
		"Owner Dashboard": "Owner Dashboard Onboarding",
		"Horse Management Dashboard": "Horse Management Onboarding",
		"Groom Dashboard": "Groom Dashboard Onboarding",
		"Money Dashboard": "Money Dashboard Onboarding",
		"Match Dashboard": "Match Dashboard Onboarding",
	};

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
		patch_workspace_onboarding_blocks();
		redirect_to_role_dashboard_if_needed();
		ensure_poloway_sidebar_if_needed();
		redirect_to_whiteboard_if_needed();
		add_owner_receipt_action_if_needed();
		open_receipt_uploader_from_route_if_needed();
		scope_sidebar_to_current_dashboard();
		patch_internal_link_navigation();

		const task_kanban = is_task_kanban_route();
		document.body.classList.toggle("pm-task-kanban", task_kanban);
		document.body.classList.toggle("pm-task-groom", task_kanban && is_limited_groom());

		if (task_kanban) {
			compact_task_kanban();
		}
	}

	function patch_workspace_onboarding_blocks() {
		const Workspace = frappe.views && frappe.views.Workspace;
		if (!Workspace || Workspace.prototype._pm_onboarding_block_patch) {
			return;
		}

		Workspace.prototype._pm_onboarding_block_patch = true;
		const original_prepare_editorjs = Workspace.prototype.prepare_editorjs;
		Workspace.prototype.prepare_editorjs = function () {
			ensure_workspace_onboarding_content(this);
			sync_onboarding_page_data(this);
			return original_prepare_editorjs.call(this);
		};
	}

	function ensure_workspace_onboarding_content(workspace) {
		const page_name = workspace && workspace._page && workspace._page.name;
		const onboarding_name = WORKSPACE_ONBOARDINGS[page_name];
		if (!onboarding_name) {
			return;
		}

		if (typeof workspace.content === "string") {
			try {
				workspace.content = JSON.parse(workspace.content);
			} catch {
				workspace.content = [];
			}
		}
		if (!Array.isArray(workspace.content)) {
			workspace.content = [];
		}

		const has_block = workspace.content.some((row) => {
			return row && row.type === "onboarding" && row.data && row.data.onboarding_name === onboarding_name;
		});
		if (!has_block) {
			workspace.content.unshift({
				type: "onboarding",
				data: {
					onboarding_name,
					col: 12,
				},
			});
		}
	}

	function sync_onboarding_page_data(workspace) {
		const config = workspace && workspace.editor && workspace.editor.configuration;
		if (
			config &&
			config.tools &&
			config.tools.onboarding &&
			config.tools.onboarding.config &&
			workspace.page_data
		) {
			config.tools.onboarding.config.page_data = workspace.page_data;
		}
	}

	function redirect_to_role_dashboard_if_needed() {
		if (frappe._pm_role_dashboard_redirecting || !is_polomanagement_home_route()) {
			return;
		}

		const target = get_role_dashboard_route();
		if (!target) {
			return;
		}

		frappe._pm_role_dashboard_redirecting = true;
		frappe.set_route(target);
		setTimeout(() => {
			frappe._pm_role_dashboard_redirecting = false;
		}, 1000);
	}

	function is_polomanagement_home_route() {
		const route_str = (frappe.get_route_str ? frappe.get_route_str() : "").toLowerCase();
		const path = window.location.pathname.replace(/\/$/, "").toLowerCase();
		return (
			route_str === "poloway" ||
			route_str === "workspaces/poloway" ||
			path.endsWith("/app/poloway") ||
			path.endsWith("/desk/poloway")
		);
	}

	function get_role_dashboard_route() {
		if (is_limited_groom()) {
			return "groom-dashboard";
		}

		return null;
	}

	function is_owner_dashboard_route() {
		const route_str = (frappe.get_route_str ? frappe.get_route_str() : "").toLowerCase();
		const path = window.location.pathname.replace(/\/$/, "").toLowerCase();
		return (
			route_str === "owner-dashboard" ||
			route_str === "workspaces/owner-dashboard" ||
			path.endsWith("/app/owner-dashboard")
		);
	}

	function is_money_dashboard_route() {
		const route_str = (frappe.get_route_str ? frappe.get_route_str() : "").toLowerCase();
		const path = window.location.pathname.replace(/\/$/, "").toLowerCase();
		return (
			route_str === "money-dashboard" ||
			route_str === "workspaces/money-dashboard" ||
			path.endsWith("/app/money-dashboard")
		);
	}

	function is_horse_management_dashboard_route() {
		const route_str = (frappe.get_route_str ? frappe.get_route_str() : "").toLowerCase();
		const path = window.location.pathname.replace(/\/$/, "").toLowerCase();
		return (
			route_str === "horse-management-dashboard" ||
			route_str === "workspaces/horse-management-dashboard" ||
			path.endsWith("/app/horse-management-dashboard")
		);
	}

	function is_match_dashboard_route() {
		const route_str = (frappe.get_route_str ? frappe.get_route_str() : "").toLowerCase();
		const path = window.location.pathname.replace(/\/$/, "").toLowerCase();
		return (
			route_str === "match-dashboard" ||
			route_str === "workspaces/match-dashboard" ||
			path.endsWith("/app/match-dashboard")
		);
	}

	function is_groom_dashboard_route() {
		const route_str = (frappe.get_route_str ? frappe.get_route_str() : "").toLowerCase();
		const path = window.location.pathname.replace(/\/$/, "").toLowerCase();
		return (
			route_str === "groom-dashboard" ||
			route_str === "workspaces/groom-dashboard" ||
			path.endsWith("/app/groom-dashboard")
		);
	}

	function is_receipt_dashboard_route() {
		return is_owner_dashboard_route() || is_money_dashboard_route() || is_polomanagement_home_route();
	}

	function ensure_poloway_sidebar_if_needed() {
		if (!should_use_poloway_sidebar()) {
			return;
		}

		setTimeout(() => {
			const sidebar = frappe.app && frappe.app.sidebar;
			const boot_sidebar = frappe.boot && frappe.boot.workspace_sidebar_item;
			if (!sidebar || !boot_sidebar || !boot_sidebar.poloway) {
				return;
			}

			remember_poloway_sidebar_for_route();
			if (sidebar.sidebar_title !== "Poloway" && typeof sidebar.setup === "function") {
				sidebar.setup("Poloway");
			}
		}, 100);
	}

	function should_use_poloway_sidebar() {
		if (
			is_polomanagement_home_route() ||
			is_owner_dashboard_route() ||
			is_money_dashboard_route() ||
			is_horse_management_dashboard_route() ||
			is_match_dashboard_route() ||
			is_groom_dashboard_route()
		) {
			return true;
		}

		const entity = current_route_entity();
		if (!entity) {
			return false;
		}

		const sidebar = frappe.boot && frappe.boot.workspace_sidebar_item && frappe.boot.workspace_sidebar_item.poloway;
		return Boolean(
			sidebar &&
				Array.isArray(sidebar.items) &&
				sidebar.items.some((item) => item && item.type === "Link" && item.link_to === entity)
		);
	}

	function current_route_entity() {
		const route = frappe.get_route ? frappe.get_route() : [];
		if (!route || !route.length) {
			return null;
		}

		if (route.length === 1) {
			return route[0];
		}
		if (route.length === 2) {
			return route[1];
		}
		if (route.length === 3 && route[0] === "Workspaces" && route[1] === "private") {
			return route[2];
		}
		return route[1] || route[0];
	}

	function remember_poloway_sidebar_for_route() {
		const entity = current_route_entity();
		if (!entity) {
			return;
		}

		let remembered = {};
		try {
			remembered = JSON.parse(localStorage.getItem("sidebar_item_map") || "{}") || {};
		} catch {
			remembered = {};
		}

		remembered[entity] = ["Poloway"];
		localStorage.setItem("sidebar_item_map", JSON.stringify(remembered));
	}

	function patch_internal_link_navigation() {
		if (frappe._pm_internal_link_navigation_patched) {
			return;
		}

		frappe._pm_internal_link_navigation_patched = true;
		document.addEventListener(
			"click",
			(event) => {
				const anchor = event.target.closest && event.target.closest("a[href]");
				if (
					!anchor ||
					event.defaultPrevented ||
					event.metaKey ||
					event.ctrlKey ||
					event.shiftKey ||
					event.altKey
				) {
					return;
				}

				const href = anchor.getAttribute("href") || "";
				if (!href || href === "#" || href.startsWith("javascript:") || href.startsWith("mailto:")) {
					return;
				}

				let url;
				try {
					url = new URL(href, window.location.origin);
				} catch {
					return;
				}

				if (url.origin !== window.location.origin) {
					return;
				}

				const match = url.pathname.match(/\/(?:app|desk)\/(.+)$/);
				if (!match) {
					return;
				}

				event.preventDefault();
				event.stopPropagation();
				anchor.removeAttribute("target");

				const route = decodeURIComponent(match[1]).replace(/\/$/, "");
				const route_parts = route.split("/").filter(Boolean);
				if (route_parts.length) {
					frappe.set_route(...route_parts);
				}

				if (
					url.search.includes("upload_receipt=1") &&
					can_upload_receipts() &&
					window.polomanagement_upload_receipts
				) {
					setTimeout(() => window.polomanagement_upload_receipts({}), 500);
				}
			},
			true
		);
	}

	function can_upload_receipts() {
		return frappe.user.has_role("Horse Owner") || frappe.user.has_role("System Manager");
	}

	function add_owner_receipt_action_if_needed() {
		if (!is_receipt_dashboard_route() || !can_upload_receipts()) {
			return;
		}

		setTimeout(() => {
			if ($(".pm-owner-upload-receipt").length) {
				return;
			}
			const $actions = $(".page-actions").first();
			if (!$actions.length) {
				return;
			}
			const $button = $(
				`<button class="btn btn-primary btn-sm pm-owner-upload-receipt">${__("Upload Receipt")}</button>`
			);
			$button.on("click", () => {
				window.polomanagement_upload_receipts({});
			});
			$actions.prepend($button);
		}, 300);
	}

	function open_receipt_uploader_from_route_if_needed() {
		if (
			frappe._pm_receipt_route_upload_opened ||
			!is_receipt_dashboard_route() ||
			!can_upload_receipts() ||
			!window.location.search.includes("upload_receipt=1")
		) {
			return;
		}
		frappe._pm_receipt_route_upload_opened = true;
		setTimeout(() => window.polomanagement_upload_receipts({}), 500);
	}

	window.polomanagement_upload_receipts = function ({ linked_horse } = {}) {
		if (!can_upload_receipts()) {
			frappe.throw(__("Only Horse Owners and System Managers can upload receipts."));
		}

		const file_urls = [];
		let processing_started = false;
		const uploader = new frappe.ui.FileUploader({
			allow_multiple: true,
			dialog_title: __("Upload Receipts"),
			folder: "Home/Attachments",
			restrictions: {
				allowed_file_types: [".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"],
			},
			on_success(file_doc) {
				const file_url = file_doc.file_url || file_doc.name;
				if (file_url && !file_urls.includes(file_url)) {
					file_urls.push(file_url);
				}
			},
		});

		const process_files = () => {
			if (processing_started || !file_urls.length) {
				return;
			}
			processing_started = true;
			frappe.call({
				method: "polomanagement.polomanagement.doctype.receipt_import.receipt_import.create_receipt_import",
				args: {
					receipt_file_urls: JSON.stringify(file_urls),
					linked_horse,
					process: 1,
				},
				freeze: true,
				freeze_message: __("Reading receipt and creating transaction..."),
				callback(r) {
					const result = r.message || {};
					if (result.transaction_input) {
						frappe.show_alert({ message: __("Transaction created from receipt."), indicator: "green" });
						frappe.set_route("Form", "Transaction Input", result.transaction_input);
					} else if (result.receipt_import) {
						frappe.set_route("Form", "Receipt Import", result.receipt_import);
					}
				},
			});
		};

		if (uploader.dialog) {
			uploader.dialog.$wrapper.on("hidden.bs.modal", process_files);
		}
	};

	function render_poloway_dashboard_if_needed() {
		if (!is_polomanagement_home_route() || is_limited_groom()) {
			return;
		}
		render_dashboard_once("poloway", "polomanagement.owner_dashboard.get_owner_home_dashboard", render_poloway_dashboard);
	}

	function render_money_dashboard_if_needed() {
		if (!is_money_dashboard_route()) {
			return;
		}
		render_dashboard_once("money", "polomanagement.owner_dashboard.get_money_dashboard", render_money_dashboard);
	}

	function render_dashboard_once(key, method, render) {
		setTimeout(() => {
			const $section = $(".layout-main-section").first();
			if (!$section.length) {
				return;
			}
			if ($section.data("pm-dashboard-key") === key) {
				return;
			}
			$section.data("pm-dashboard-key", key);
			$section.html(`<div class="pm-dashboard-shell"><div class="pm-dashboard-loading">${__("Loading dashboard...")}</div></div>`);
			frappe.call({
				method,
				callback(r) {
					const data = r.message || {};
					$section.html(render(data));
					bind_dashboard_actions($section);
				},
			});
		}, 250);
	}

	function render_poloway_dashboard(data) {
		const financial = data.financial || {};
		const month = financial.month || {};
		const year = financial.year || {};
		const polo = data.polo || {};
		const horses = data.horses || {};
		const actions = data.actions || {};

		return `
			<div class="pm-dashboard-shell pm-poloway-dashboard">
				<section class="pm-dashboard-hero">
					<div>
						<div class="pm-dashboard-kicker">${__("Poloway Overview")}</div>
						<h1>${__("Owner Command Center")}</h1>
						<p>${__("Money, polo schedule, horse performance, and owner actions in one calm view.")}</p>
					</div>
					<div class="pm-hero-metrics">
						${dashboard_metric(__("Month Net"), money(month.net), month.net >= 0 ? "good" : "bad")}
						${dashboard_metric(__("YTD Net"), money(year.net), year.net >= 0 ? "good" : "bad")}
						${dashboard_metric(__("Open Issues"), actions.open_issues ? actions.open_issues.length : 0, actions.open_issues && actions.open_issues.length ? "warn" : "good")}
					</div>
				</section>

				<section class="pm-dashboard-grid pm-dashboard-grid-main">
					${panel(__("Financial Picture"), financial_picture(financial), "pm-panel-large")}
					${panel(__("Quick Money Actions"), quick_money_actions(), "pm-panel-side")}
				</section>

				<section class="pm-dashboard-grid">
					${panel(__("Upcoming Polo"), polo_card(polo), "pm-panel-large")}
					${panel(__("Owner Actions"), owner_actions_card(actions), "pm-panel-side")}
				</section>

				<section class="pm-dashboard-grid">
					${panel(__("Horse Performance"), horse_performance_card(horses), "pm-panel-large")}
					${panel(__("Care Signals"), care_signals_card(horses), "pm-panel-side")}
				</section>
			</div>
		`;
	}

	function render_money_dashboard(data) {
		const financial = data.financial || {};
		const operations = data.operations || {};
		const inventory = data.inventory || {};
		const vendors = data.vendors || {};

		return `
			<div class="pm-dashboard-shell pm-money-dashboard">
				<section class="pm-dashboard-hero pm-money-hero">
					<div>
						<div class="pm-dashboard-kicker">${__("Money Dashboard")}</div>
						<h1>${__("Finance, Receipts, Inventory")}</h1>
						<p>${__("One entry point for transactions, receipts, purchases, items, vendors, and stock movement.")}</p>
					</div>
					<div class="pm-hero-metrics">
						${dashboard_metric(__("Month Out"), money((financial.month || {}).outflow), "bad")}
						${dashboard_metric(__("Month In"), money((financial.month || {}).income), "good")}
						${dashboard_metric(__("Unposted"), financial.unposted || 0, financial.unposted ? "warn" : "good")}
					</div>
				</section>

				<section class="pm-dashboard-grid pm-dashboard-grid-main">
					${panel(__("Money Flow"), financial_picture(financial), "pm-panel-large")}
					${panel(__("Money Actions"), money_action_stack(), "pm-panel-side")}
				</section>

				<section class="pm-dashboard-grid">
					${panel(__("Purchases and Quotes"), purchase_quote_card(operations), "pm-panel-large")}
					${panel(__("Inventory"), inventory_card(inventory), "pm-panel-side")}
				</section>

				<section class="pm-dashboard-grid">
					${panel(__("Recent Transactions"), transaction_rows((financial.recent || [])), "pm-panel-large")}
					${panel(__("Vendors"), vendor_card(vendors), "pm-panel-side")}
				</section>
			</div>
		`;
	}

	function financial_picture(financial) {
		const month = financial.month || {};
		const year = financial.year || {};
		return `
			<div class="pm-finance-summary">
				${dashboard_metric(__("Month Income"), money(month.income), "good")}
				${dashboard_metric(__("Month Outflow"), money(month.outflow), "bad")}
				${dashboard_metric(__("Month Net"), money(month.net), month.net >= 0 ? "good" : "bad")}
				${dashboard_metric(__("YTD Net"), money(year.net), year.net >= 0 ? "good" : "bad")}
			</div>
			${bar_chart(financial.trend || [], "period", [
				{ field: "income", label: __("Income"), className: "pm-bar-good" },
				{ field: "outflow", label: __("Outflow"), className: "pm-bar-bad" },
			])}
			${category_bars(financial.categories || [])}
		`;
	}

	function quick_money_actions() {
		return `
			<div class="pm-action-stack">
				${action_button(__("Open Money Dashboard"), "money-dashboard", "primary")}
				${action_button(__("Upload Receipt"), "upload-receipt")}
				${action_button(__("New Transaction"), "new-transaction")}
				${action_button(__("Financial Ledger"), "financial-ledger")}
			</div>
		`;
	}

	function money_action_stack() {
		return `
			<div class="pm-action-stack">
				${action_button(__("Upload Receipt"), "upload-receipt", "primary")}
				${action_button(__("New Transaction"), "new-transaction")}
				${action_button(__("New Purchase"), "new-purchase")}
				${action_button(__("Financial Ledger"), "financial-ledger")}
				${action_button(__("Items"), "items")}
				${action_button(__("Vendors"), "vendors")}
			</div>
		`;
	}

	function polo_card(polo) {
		const next = polo.next_match;
		return `
			${next ? `
				<div class="pm-next-card">
					<div class="pm-next-date">${date_label(next.match_date)}</div>
					<div>
						<div class="pm-next-title">${esc(next.event_name)}</div>
						<div class="pm-next-meta">${esc([next.team, next.opponent].filter(Boolean).join(" vs ")) || __("Team not set")}</div>
						<div class="pm-next-meta">${esc(next.venue || __("Venue not set"))}</div>
					</div>
				</div>
			` : empty_state(__("No upcoming match days yet."))}
			${list_rows((polo.upcoming || []).slice(0, 5), (row) => ({
				label: row.event_name,
				meta: [row.match_date, row.venue, row.status].filter(Boolean).join(" / "),
				route: ["Form", "Match Day", row.name],
			}))}
			${pill_chart(polo.status_counts || [], "status", "count")}
		`;
	}

	function owner_actions_card(actions) {
		return `
			<div class="pm-finance-summary pm-two-metrics">
				${dashboard_metric(__("Groom Open"), (actions.groom_today || {}).open || 0, ((actions.groom_today || {}).open || 0) ? "warn" : "good")}
				${dashboard_metric(__("Groom Done"), (actions.groom_today || {}).completed || 0, "good")}
			</div>
			${list_rows(actions.open_tasks || [], (row) => ({
				label: row.subject,
				meta: [row.due_date, row.priority, row.task_type].filter(Boolean).join(" / "),
				route: ["Form", "Owner Task", row.name],
			}))}
			<div class="pm-action-stack pm-action-stack-tight">
				${action_button(__("Owner Calendar"), "owner-calendar")}
				${action_button(__("Owner Gantt"), "owner-gantt")}
			</div>
		`;
	}

	function horse_performance_card(horses) {
		const counts = horses.counts || {};
		return `
			<div class="pm-finance-summary">
				${dashboard_metric(__("Horses"), counts.total || 0, "neutral")}
				${dashboard_metric(__("Available"), counts.available || 0, "good")}
				${dashboard_metric(__("Need Attention"), counts.attention || 0, counts.attention ? "warn" : "good")}
				${dashboard_metric(__("Training 30d"), counts.training_30d || 0, "neutral")}
			</div>
			${bar_chart(horses.top_training || [], "horse_name", [
				{ field: "completed", label: __("Completed"), className: "pm-bar-good" },
				{ field: "follow_up", label: __("Follow Up"), className: "pm-bar-warn" },
			])}
			<div class="pm-action-stack pm-action-stack-tight">
				${action_button(__("Open Horses"), "horses")}
				${action_button(__("Training Report"), "training-report")}
				${action_button(__("Compliance"), "compliance-report")}
			</div>
		`;
	}

	function care_signals_card(horses) {
		return `
			${pill_chart(horses.readiness || [], "status", "count")}
			${list_rows(horses.issues || [], (row) => ({
				label: row.subject,
				meta: [row.issue_priority, row.issue_status, row.horse].filter(Boolean).join(" / "),
				route: ["Form", "Task", row.name],
			}))}
		`;
	}

	function purchase_quote_card(operations) {
		return `
			<div class="pm-split-list">
				<div>
					<div class="pm-mini-heading">${__("Purchases")}</div>
					${list_rows(operations.purchases || [], (row) => ({
						label: row.purchase_title || row.name,
						meta: [row.status, row.needed_by, money(row.estimated_total)].filter(Boolean).join(" / "),
						route: ["Form", "Purchase", row.name],
					}))}
				</div>
				<div>
					<div class="pm-mini-heading">${__("Quotes")}</div>
					${list_rows(operations.quotes || [], (row) => ({
						label: row.quote_title || row.name,
						meta: [row.status, row.vendor, money(row.total_amount)].filter(Boolean).join(" / "),
						route: ["Form", "Vendor Quote", row.name],
					}))}
				</div>
			</div>
		`;
	}

	function inventory_card(inventory) {
		return `
			<div class="pm-finance-summary pm-three-metrics">
				${dashboard_metric(__("Items"), inventory.items || 0, "neutral")}
				${dashboard_metric(__("Locations"), inventory.locations || 0, "neutral")}
				${dashboard_metric(__("Categories"), inventory.categories || 0, "neutral")}
			</div>
			${list_rows(inventory.recent_stock || [], (row) => ({
				label: row.item,
				meta: [row.posting_date, row.movement_type, row.quantity_change].filter(Boolean).join(" / "),
				route: ["Form", "Item Stock Ledger", row.name],
			}))}
		`;
	}

	function vendor_card(vendors) {
		return `
			<div class="pm-finance-summary pm-two-metrics">
				${dashboard_metric(__("Vendors"), vendors.vendors || 0, "neutral")}
				${dashboard_metric(__("Active Quotes"), vendors.active_quotes || 0, vendors.active_quotes ? "warn" : "good")}
			</div>
			${list_rows(vendors.recent_vendors || [], (row) => ({
				label: row.vendor_name || row.name,
				meta: [row.vendor_type, row.phone, row.email].filter(Boolean).join(" / "),
				route: ["Form", "Vendor", row.name],
			}))}
		`;
	}

	function transaction_rows(rows) {
		return list_rows(rows, (row) => ({
			label: [row.transaction_category, money(row.total_amount)].filter(Boolean).join(" / "),
			meta: [row.transaction_date, row.direction, row.transaction_type].filter(Boolean).join(" / "),
			route: ["Form", "Transaction Input", row.name],
		}));
	}

	function panel(title, body, className) {
		return `
			<div class="pm-dashboard-panel ${className || ""}">
				<header>${esc(title)}</header>
				<div class="pm-dashboard-panel-body">${body}</div>
			</div>
		`;
	}

	function dashboard_metric(label, value, tone) {
		return `
			<div class="pm-dashboard-metric pm-tone-${tone || "neutral"}">
				<div class="pm-dashboard-metric-value">${esc(value)}</div>
				<div class="pm-dashboard-metric-label">${esc(label)}</div>
			</div>
		`;
	}

	function bar_chart(rows, labelField, series) {
		if (!rows.length) {
			return empty_state(__("No chart data yet."));
		}
		const max = Math.max(
			1,
			...rows.flatMap((row) => series.map((item) => Math.abs(Number(row[item.field] || 0))))
		);
		return `
			<div class="pm-bar-chart">
				${rows.map((row) => `
					<div class="pm-bar-row">
						<div class="pm-bar-label">${esc(row[labelField] || "")}</div>
						<div class="pm-bar-track">
							${series.map((item) => `
								<span class="pm-bar ${item.className}" style="width:${Math.max(3, (Math.abs(Number(row[item.field] || 0)) / max) * 100)}%" title="${esc(item.label)}"></span>
							`).join("")}
						</div>
					</div>
				`).join("")}
			</div>
			<div class="pm-chart-legend">
				${series.map((item) => `<span><i class="${item.className}"></i>${esc(item.label)}</span>`).join("")}
			</div>
		`;
	}

	function category_bars(rows) {
		if (!rows.length) {
			return "";
		}
		const max = Math.max(1, ...rows.map((row) => Number(row.total || 0)));
		return `
			<div class="pm-category-bars">
				${rows.slice(0, 5).map((row) => `
					<div class="pm-category-row">
						<span>${esc(row.category || __("Other"))}</span>
						<div><i class="${row.direction === "Money In" ? "pm-bar-good" : "pm-bar-bad"}" style="width:${Math.max(4, (Number(row.total || 0) / max) * 100)}%"></i></div>
						<strong>${money(row.total)}</strong>
					</div>
				`).join("")}
			</div>
		`;
	}

	function pill_chart(rows, labelField, valueField) {
		if (!rows.length) {
			return "";
		}
		return `
			<div class="pm-pill-chart">
				${rows.map((row) => `
					<span>${esc(row[labelField] || __("Not Set"))}<strong>${esc(row[valueField] || 0)}</strong></span>
				`).join("")}
			</div>
		`;
	}

	function list_rows(rows, mapper) {
		if (!rows || !rows.length) {
			return empty_state(__("Nothing needs attention here."));
		}
		return `
			<div class="pm-dashboard-list">
				${rows.map((row) => {
					const item = mapper(row);
					return `
						<a class="pm-dashboard-row" href="#" data-route='${JSON.stringify(item.route || [])}'>
							<span class="pm-dashboard-row-main">${esc(item.label || "")}</span>
							<span class="pm-dashboard-row-meta">${esc(item.meta || "")}</span>
						</a>
					`;
				}).join("")}
			</div>
		`;
	}

	function action_button(label, action, tone) {
		return `<button class="btn btn-${tone === "primary" ? "primary" : "default"} btn-sm pm-dashboard-action" data-action="${esc(action)}">${esc(label)}</button>`;
	}

	function empty_state(message) {
		return `<div class="pm-dashboard-empty">${esc(message)}</div>`;
	}

	function bind_dashboard_actions($section) {
		$section.find(".pm-dashboard-row").on("click", function (event) {
			event.preventDefault();
			const route = JSON.parse($(this).attr("data-route") || "[]");
			if (route.length) {
				frappe.set_route(...route);
			}
		});

		$section.find(".pm-dashboard-action").on("click", function () {
			const action = $(this).data("action");
			if (action === "upload-receipt") {
				window.polomanagement_upload_receipts({});
			} else if (action === "money-dashboard") {
				frappe.set_route("money-dashboard");
			} else if (action === "new-transaction") {
				frappe.new_doc("Transaction Input");
			} else if (action === "new-purchase") {
				frappe.new_doc("Purchase");
			} else if (action === "financial-ledger") {
				frappe.set_route("query-report", "Financial Ledger");
			} else if (action === "owner-calendar") {
				frappe.set_route("List", "Owner Task", "Calendar");
			} else if (action === "owner-gantt") {
				frappe.set_route("owner-task", "view", "gantt");
			} else if (action === "horses") {
				frappe.set_route("List", "Horse", "List");
			} else if (action === "training-report") {
				frappe.set_route("query-report", "Horse Training Records");
			} else if (action === "compliance-report") {
				frappe.set_route("query-report", "Horse Compliance Alerts");
			} else if (action === "items") {
				frappe.set_route("List", "Item", "List");
			} else if (action === "vendors") {
				frappe.set_route("List", "Vendor", "List");
			}
		});
	}

	function scope_sidebar_to_current_dashboard() {
		setTimeout(() => {
			$(".standard-sidebar-item, .desk-sidebar-item, .sidebar-item").show();
		}, 350);
	}

	function get_sidebar_scope() {
		if (is_limited_groom()) {
			return "groom";
		}
		if (is_horse_management_dashboard_route()) {
			return "horse";
		}
		if (is_match_dashboard_route()) {
			return "match";
		}
		if (is_money_dashboard_route()) {
			return "money";
		}
		if (is_owner_dashboard_route()) {
			return "owner";
		}
		if (is_polomanagement_home_route()) {
			return "home";
		}
		return null;
	}

	function sidebar_labels_for_scope(scope) {
		const common = [
			"Poloway Home",
			"Owner Dashboard",
			"Money Dashboard",
			"Horse Management Dashboard",
			"Match Dashboard",
		];
		const labels = {
			home: common.concat([
				"Owner Actions", "Owner Calendar", "Owner Issues",
				"Horse Operations", "Horses", "Horse Performance Summary",
				"Match Operations", "Match Days", "Upcoming Polo Schedule", "Polo Performance Summary",
			]),
			owner: common.concat([
				"Owner Actions", "Owner Calendar", "Owner Issues", "Schedule Settings", "Task Templates",
				"Horse Operations", "Horses", "Match Day", "Match Day Board", "Horse Tack Configuration",
				"Travel Manifest", "Horse Feeding Records", "Horse Training Records", "Horse Medical Records",
				"Horse Compliance Alerts", "Groom Profile", "Horse Owner",
			]),
			horse: common.concat([
				"Horse Operations", "Horses", "Horse Performance Summary", "Horse Feeding Records",
				"Horse Training Records", "Horse Medical Records", "Horse Compliance Alerts",
				"Horse Care Entry", "Horse Training Template", "Groom Profile", "Horse Owner",
				"Money", "Horse Expenses", "Transaction Input",
			]),
			match: common.concat([
				"Match Operations", "Match Days", "Upcoming Polo Schedule", "Polo Performance Summary",
				"Match Day Board", "Travel Manifest", "Horse Tack Configuration",
				"Owner Actions", "Owner Calendar", "Today Tasks", "Task List",
			]),
			money: common.concat([
				"Money", "Transaction Input", "Receipt Import", "Purchase", "Vendor Quote",
				"Vendor", "Item", "Item Category", "Inventory Location", "Stock Adjustment",
				"Employees / Grooms", "Autopayments", "Money Account",
			]),
			groom: ["Groom Dashboard", "Groom Work", "Today Tasks", "Task List", "Horse Care Entry", "Horse Operations", "Match Day", "Match Day Board", "Travel Manifest", "Horse Feeding Records", "Horse Training Records", "Horse Medical Records", "Horses"],
		};
		return new Set(labels[scope] || []);
	}

	function sidebar_label($item) {
		const text = ($item.find(".sidebar-item-label, .item-label, .ellipsis").first().text() || $item.text() || "")
			.replace(/\s+/g, " ")
			.trim();
		return text;
	}

	function money(value) {
		const number = Number(value);
		const safe_number = Number.isFinite(number) ? number : 0;
		if (typeof format_currency === "function") {
			const formatted = format_currency(safe_number);
			if (formatted && !String(formatted).includes("NaN")) {
				return formatted;
			}
		}
		const currency = (frappe.boot && frappe.boot.sysdefaults && frappe.boot.sysdefaults.currency) || "ZAR";
		return new Intl.NumberFormat(undefined, {
			style: "currency",
			currency,
			maximumFractionDigits: 0,
		}).format(safe_number);
	}

	function date_label(value) {
		return value ? frappe.datetime.str_to_user(value) : "";
	}

	function esc(value) {
		return frappe.utils.escape_html(String(value == null ? "" : value));
	}

	function redirect_to_whiteboard_if_needed() {
		const route = frappe.get_route();
		if (!route || route.length < 4) {
			return;
		}

		const route_prefix = route.slice(0, 3).map((part) => String(part || "").toLowerCase()).join("/");
		const board_name = String(route[3] || "");
		const is_task_kanban =
			route_prefix === "task/view/kanban" || route_prefix === "list/task/kanban";

		if (is_task_kanban && board_name !== "Whiteboard") {
			frappe.set_route(route[0], route[1], route[2], "Whiteboard");
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
				{
					fieldname: "issue_priority",
					fieldtype: "Select",
					label: __("Issue Priority"),
					options: "Low\nNormal\nHigh\nUrgent",
					default: "Normal",
					depends_on: "eval:doc.issue_reported",
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
						issue_priority: values.issue_priority,
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
