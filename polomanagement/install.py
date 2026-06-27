import frappe


def after_migrate():
	setup_task_kanban()
	setup_inventory()
	setup_ledgers()
	setup_money_reports()
	cleanup_legacy_polomanagement_desktop()
	setup_desktop()


def setup_task_kanban():
	frappe.db.set_value(
		"DocType",
		"Task",
		{
			"default_view": "Kanban",
			"force_re_route_to_default_view": 0,
		},
		update_modified=False,
	)

	board_name = "Whiteboard"
	if frappe.db.exists("Kanban Board", board_name):
		board = frappe.get_doc("Kanban Board", board_name)
	else:
		board = frappe.new_doc("Kanban Board")
		board.kanban_board_name = board_name

	board.reference_doctype = "Task"
	board.field_name = "status"
	board.private = 0
	board.show_labels = 0
	board.fields = frappe.as_json([])
	board.filters = None
	set_kanban_columns(board)
	board.save(ignore_permissions=True)
	remove_extra_task_kanban_boards(board_name)


def remove_extra_task_kanban_boards(keep_board):
	for board_name in frappe.get_all(
		"Kanban Board",
		filters={"reference_doctype": "Task"},
		pluck="name",
	):
		if board_name != keep_board:
			frappe.delete_doc("Kanban Board", board_name, ignore_permissions=True, force=True)


def set_kanban_columns(board):
	columns = [
		("Open", "Blue"),
		("Completed", "Green"),
		("Cancelled", "Gray"),
	]

	board.columns = []
	for column_name, indicator in columns:
		board.append(
			"columns",
			{
				"column_name": column_name,
				"status": "Active",
				"indicator": indicator,
				"order": "[]",
			},
		)


def setup_desktop():
	remove_owner_number_cards()
	setup_dashboard_widgets()
	setup_workspaces()
	setup_workspace_sidebar()
	setup_desktop_icon()


def cleanup_legacy_polomanagement_desktop():
	for doctype, name in [
		("Desktop Icon", "Polomanagement"),
		("Workspace Sidebar", "Polomanagement"),
		("Workspace", "Polomanagement"),
	]:
		frappe.delete_doc_if_exists(doctype, name, force=True)


def setup_workspaces():
	upsert_workspace(
		"Poloway",
		{
			"title": "Poloway",
			"icon": "flag",
			"indicator_color": "blue",
			"roles": ["Horse Owner", "Stable Manager", "System Manager"],
			"shortcuts": [
				url_shortcut("Owner Dashboard", "/app/owner-dashboard", icon="layout-dashboard"),
				url_shortcut("Money Dashboard", "/app/money-dashboard", icon="circle-dollar-sign"),
				shortcut("Money Flow", "Report", "Money Flow Summary", icon="chart-column"),
				shortcut("Polo Performance", "Report", "Polo Performance Summary", icon="trophy"),
				shortcut("Horse Performance", "Report", "Horse Performance Summary", icon="activity"),
				shortcut("Owner Calendar", "DocType", "Owner Task", doc_view="Calendar", icon="calendar-days"),
				url_shortcut("Upload Receipt", "/app/owner-dashboard?upload_receipt=1", icon="receipt-text"),
				shortcut("Horses", "DocType", "Horse", doc_view="List", icon="heart-handshake"),
				shortcut("Match Days", "DocType", "Match Day", doc_view="List", icon="flag"),
				shortcut("Match Board", "Report", "Match Day Board", icon="columns-3"),
			],
			"number_cards": [
				number_card("Income"),
				number_card("Outflow"),
				number_card("Net Cash Flow"),
				number_card("Open Actions"),
				number_card("Open Issues"),
				number_card("Medical Due"),
			],
			"charts": [
				chart("Money Flow"),
				chart("Spending Breakdown"),
				chart("Polo Performance"),
				chart("Horse Readiness"),
			],
			"links": [
				card("Big Picture"),
				link("Money Flow Summary", "Report"),
				link("Spending By Category", "Report"),
				link("Financial Overview", "Report"),
				link("Polo Performance Summary", "Report"),
				link("Match Day Board", "Report"),
				card("Owner Actions"),
				link("Owner Task", "DocType"),
				link("Owner Action Summary", "Report"),
				link("Owner Task Issues", "Report"),
				card("Tournaments"),
				link("Match Day", "DocType"),
				link("Match Day Board", "Report"),
				card("Horse Performance"),
				link("Horse", "DocType"),
				link("Horse Performance Summary", "Report"),
				link("Horse Training Records", "Report"),
				link("Horse Compliance Alerts", "Report"),
			],
			"content": [
				content("number_card", "Income", col=2),
				content("number_card", "Outflow", col=2),
				content("number_card", "Net Cash Flow", col=2),
				content("number_card", "Open Actions", col=2),
				content("number_card", "Open Issues", col=2),
				content("number_card", "Medical Due", col=2),
				content("chart", "Money Flow", col=6),
				content("chart", "Spending Breakdown", col=6),
				content("chart", "Polo Performance", col=6),
				content("chart", "Horse Readiness", col=6),
				spacer(),
				content("shortcut", "Owner Dashboard", col=3),
				content("shortcut", "Money Dashboard", col=3),
				content("shortcut", "Money Flow", col=3),
				content("shortcut", "Polo Performance", col=3),
				content("shortcut", "Horse Performance", col=3),
				content("shortcut", "Owner Calendar", col=3),
				content("shortcut", "Upload Receipt", col=3),
				content("shortcut", "Horses", col=3),
				content("shortcut", "Match Days", col=3),
				content("shortcut", "Match Board", col=3),
				spacer(),
				content("card", "Big Picture", col=4),
				content("card", "Owner Actions", col=4),
				content("card", "Tournaments", col=4),
				content("card", "Horse Performance", col=4),
			],
		},
	)

	upsert_workspace(
		"Groom Dashboard",
		{
			"title": "Groom Dashboard",
			"icon": "list-todo",
			"indicator_color": "green",
			"parent_page": "Poloway",
			"roles": ["Horse Groom", "Stable Manager", "System Manager"],
			"shortcuts": [
				task_whiteboard_shortcut(),
				shortcut("Task List", "DocType", "Task", doc_view="List", icon="list"),
				shortcut("Task Calendar", "DocType", "Task", doc_view="Calendar", icon="calendar-days"),
				shortcut("Horse Care Entry", "DocType", "Horse Care Entry", doc_view="New", icon="clipboard-plus"),
				shortcut("Match Days", "DocType", "Match Day", doc_view="List", icon="flag"),
				shortcut("Match Board", "Report", "Match Day Board", icon="columns-3"),
				shortcut("Travel", "DocType", "Travel Manifest", doc_view="List", icon="truck"),
			],
			"links": [
				card("My Work"),
				link("Task", "DocType"),
				link("Horse Care Entry", "DocType"),
				card("Polo Operations"),
				link("Match Day", "DocType"),
				link("Match Day Board", "Report"),
				link("Horse Tack Configuration", "DocType"),
				link("Travel Manifest", "DocType"),
				card("Records"),
				link("Horse Feeding Record", "DocType"),
				link("Horse Training Record", "DocType"),
				link("Horse Medical Record", "DocType"),
				link("Horse", "DocType"),
			],
			"number_cards": [],
			"charts": [],
			"content": [
				content("shortcut", "Today Tasks", col=3),
				content("shortcut", "Task List", col=3),
				content("shortcut", "Task Calendar", col=3),
				content("shortcut", "Horse Care Entry", col=3),
				content("shortcut", "Match Days", col=3),
				content("shortcut", "Match Board", col=3),
				content("shortcut", "Travel", col=3),
				spacer(),
				content("card", "My Work", col=6),
				content("card", "Polo Operations", col=6),
				content("card", "Records", col=6),
			],
		},
	)

	upsert_workspace(
		"Owner Dashboard",
		{
			"title": "Owner Dashboard",
			"icon": "layout-dashboard",
			"indicator_color": "orange",
			"parent_page": "Poloway",
			"roles": ["Horse Owner", "Stable Manager", "System Manager"],
			"shortcuts": [
				shortcut("Owner Actions", "Report", "Owner Action Summary", icon="list-checks"),
				task_whiteboard_shortcut(),
				shortcut("Owner Calendar", "DocType", "Owner Task", doc_view="Calendar", icon="calendar-days"),
				url_shortcut("Owner Gantt", "/app/owner-task/view/gantt", icon="gantt-chart"),
				shortcut("Issues", "Report", "Owner Task Issues", icon="circle-alert"),
				shortcut("Schedule Settings", "DocType", "Task Schedule Settings", icon="settings"),
				shortcut("Task Templates", "DocType", "Task Template", doc_view="List", icon="copy-check"),
				shortcut("Horses", "DocType", "Horse", doc_view="List", icon="heart-handshake"),
				shortcut("Horse Performance", "Report", "Horse Performance Summary", icon="activity"),
				shortcut("Compliance", "Report", "Horse Compliance Alerts", icon="shield-alert"),
				shortcut("Match Days", "DocType", "Match Day", doc_view="List", icon="flag"),
				shortcut("Polo Performance", "Report", "Polo Performance Summary", icon="trophy"),
				shortcut("Match Board", "Report", "Match Day Board", icon="columns-3"),
				shortcut("Travel", "DocType", "Travel Manifest", doc_view="List", icon="truck"),
				url_shortcut("Money Dashboard", "/app/money-dashboard", icon="circle-dollar-sign"),
			],
			"number_cards": [
				number_card("Open Actions"),
				number_card("Open Issues"),
				number_card("Medical Due"),
				number_card("Training Sessions"),
			],
			"charts": [
				chart("Owner Actions"),
				chart("Horse Readiness"),
				chart("Polo Performance"),
			],
			"links": [
				card("Owner Actions"),
				link("Owner Task", "DocType"),
				link("Owner Action Summary", "Report"),
				link("Owner Task Issues", "Report"),
				card("Planning"),
				link("Task Schedule Settings", "DocType"),
				link("Task Template", "DocType"),
				link("Task", "DocType"),
				card("Polo Operations"),
				link("Match Day", "DocType"),
				link("Polo Performance Summary", "Report"),
				link("Match Day Board", "Report"),
				link("Horse Tack Configuration", "DocType"),
				link("Travel Manifest", "DocType"),
				card("Horse Oversight"),
				link("Horse", "DocType"),
				link("Horse Owner", "DocType"),
				link("Groom Profile", "DocType"),
				link("Horse Performance Summary", "Report"),
				link("Horse Feeding Records", "Report"),
				link("Horse Training Records", "Report"),
				link("Horse Medical Records", "Report"),
				link("Horse Compliance Alerts", "Report"),
				card("Setup"),
				link("Horse Training Template", "DocType"),
			],
			"content": [
				content("number_card", "Open Actions", col=3),
				content("number_card", "Open Issues", col=3),
				content("number_card", "Medical Due", col=3),
				content("number_card", "Training Sessions", col=3),
				content("chart", "Owner Actions", col=6),
				content("chart", "Horse Readiness", col=6),
				content("chart", "Polo Performance", col=12),
				spacer(),
				content("shortcut", "Owner Actions", col=3),
				content("shortcut", "Today Tasks", col=3),
				content("shortcut", "Owner Calendar", col=3),
				content("shortcut", "Owner Gantt", col=3),
				content("shortcut", "Issues", col=3),
				content("shortcut", "Horses", col=3),
				content("shortcut", "Horse Performance", col=3),
				content("shortcut", "Compliance", col=3),
				content("shortcut", "Match Days", col=3),
				content("shortcut", "Polo Performance", col=3),
				content("shortcut", "Match Board", col=3),
				content("shortcut", "Travel", col=3),
				content("shortcut", "Money Dashboard", col=3),
				spacer(),
				content("card", "Owner Actions", col=4),
				content("card", "Horse Oversight", col=4),
				content("card", "Planning", col=4),
				content("card", "Polo Operations", col=4),
				content("card", "Setup", col=4),
			],
		},
	)

	upsert_workspace(
		"Money Dashboard",
		{
			"title": "Money Dashboard",
			"icon": "circle-dollar-sign",
			"indicator_color": "green",
			"parent_page": "Poloway",
			"roles": ["Horse Owner", "Stable Manager", "System Manager"],
			"shortcuts": [
				shortcut("Money Flow", "Report", "Money Flow Summary", icon="chart-column"),
				shortcut("Spending", "Report", "Spending By Category", icon="pie-chart"),
				shortcut("Financial Overview", "Report", "Financial Overview", icon="chart-column"),
				shortcut("Financial Ledger", "Report", "Financial Ledger", icon="book-open"),
				shortcut("Transactions", "DocType", "Transaction Input", doc_view="List", icon="circle-dollar-sign"),
				url_shortcut("Upload Receipt", "/app/money-dashboard?upload_receipt=1", icon="receipt-text"),
				shortcut("Purchases", "DocType", "Purchase", doc_view="List", icon="shopping-cart"),
				shortcut("Quotes", "Report", "Quote Comparison", icon="scale"),
				shortcut("Unposted", "Report", "Unposted Transactions", icon="file-clock"),
				shortcut("Items", "DocType", "Item", doc_view="List", icon="package"),
				shortcut("Inventory Summary", "Report", "Inventory Vendor Summary", icon="boxes"),
				shortcut("Vendors", "DocType", "Vendor", doc_view="List", icon="store"),
				shortcut("Locations", "DocType", "Inventory Location", doc_view="Tree", icon="warehouse"),
			],
			"number_cards": [
				number_card("Income"),
				number_card("Outflow"),
				number_card("Net Cash Flow"),
				number_card("Stock Value"),
				number_card("Open Quotes"),
			],
			"charts": [
				chart("Money Flow"),
				chart("Spending Breakdown"),
				chart("Inventory Value"),
			],
			"links": [
				card("Money Flow"),
				link("Money Flow Summary", "Report"),
				link("Spending By Category", "Report"),
				link("Transaction Input", "DocType"),
				link("Financial Overview", "Report"),
				link("Financial Ledger", "Report"),
				link("Unposted Transactions", "Report"),
				card("Receipts and Purchases"),
				link("Receipt Import", "DocType"),
				link("Purchase", "DocType"),
				link("Vendor Quote", "DocType"),
				link("Quote Comparison", "Report"),
				card("Inventory and Vendors"),
				link("Item", "DocType"),
				link("Item Category", "DocType"),
				link("Inventory Vendor Summary", "Report"),
				link("Inventory Location", "DocType"),
				link("Stock Adjustment", "DocType"),
				link("Item Stock Ledger", "Report"),
				link("Vendor", "DocType"),
				card("Money Setup"),
				link("Autopayments", "DocType"),
				link("Money Account", "DocType"),
				link("Horse Expenses", "Report"),
				link("Item Cost History", "Report"),
			],
			"content": [
				content("number_card", "Income", col=2),
				content("number_card", "Outflow", col=2),
				content("number_card", "Net Cash Flow", col=2),
				content("number_card", "Stock Value", col=3),
				content("number_card", "Open Quotes", col=3),
				content("chart", "Money Flow", col=6),
				content("chart", "Spending Breakdown", col=6),
				content("chart", "Inventory Value", col=12),
				spacer(),
				content("shortcut", "Money Flow", col=3),
				content("shortcut", "Spending", col=3),
				content("shortcut", "Financial Overview", col=3),
				content("shortcut", "Financial Ledger", col=3),
				content("shortcut", "Transactions", col=3),
				content("shortcut", "Upload Receipt", col=3),
				content("shortcut", "Purchases", col=3),
				content("shortcut", "Quotes", col=3),
				content("shortcut", "Unposted", col=3),
				content("shortcut", "Items", col=3),
				content("shortcut", "Inventory Summary", col=3),
				content("shortcut", "Vendors", col=3),
				content("shortcut", "Locations", col=3),
				spacer(),
				content("card", "Money Flow", col=4),
				content("card", "Receipts and Purchases", col=4),
				content("card", "Inventory and Vendors", col=4),
				content("card", "Money Setup", col=4),
			],
		},
	)


def setup_workspace_sidebar():
	sidebar = get_or_new("Workspace Sidebar", "Poloway")
	sidebar.title = "Poloway"
	sidebar.header_icon = "flag"
	sidebar.module = "Polomanagement"
	sidebar.app = "polomanagement"
	sidebar.standard = 1
	sidebar.items = []

	for item in [
		sidebar_link("Poloway Home", "Workspace", "Poloway", icon="home"),
		sidebar_link("Owner Dashboard", "Workspace", "Owner Dashboard", icon="layout-dashboard"),
		sidebar_link("Money Dashboard", "Workspace", "Money Dashboard", icon="circle-dollar-sign"),
		sidebar_link("Groom Dashboard", "Workspace", "Groom Dashboard", icon="list-todo"),
		sidebar_section("Owner Actions"),
		sidebar_link("Owner Calendar", "DocType", "Owner Task", icon="calendar-days", child=1),
		sidebar_link("Owner Action Summary", "Report", "Owner Action Summary", child=1),
		sidebar_link("Owner Issues", "Report", "Owner Task Issues", icon="circle-alert", child=1),
		sidebar_link("Schedule Settings", "DocType", "Task Schedule Settings", icon="settings", child=1),
		sidebar_link("Task Templates", "DocType", "Task Template", icon="copy-check", child=1),
		sidebar_section("Horse Operations"),
		sidebar_link("Horses", "DocType", "Horse", icon="heart-handshake", child=1),
		sidebar_link("Horse Performance Summary", "Report", "Horse Performance Summary", child=1),
		sidebar_link("Match Day", "DocType", "Match Day", child=1),
		sidebar_link("Polo Performance Summary", "Report", "Polo Performance Summary", child=1),
		sidebar_link("Match Day Board", "Report", "Match Day Board", child=1),
		sidebar_link("Horse Tack Configuration", "DocType", "Horse Tack Configuration", child=1),
		sidebar_link("Travel Manifest", "DocType", "Travel Manifest", child=1),
		sidebar_link("Horse Feeding Records", "Report", "Horse Feeding Records", child=1),
		sidebar_link("Horse Training Records", "Report", "Horse Training Records", child=1),
		sidebar_link("Horse Medical Records", "Report", "Horse Medical Records", child=1),
		sidebar_link("Horse Compliance Alerts", "Report", "Horse Compliance Alerts", child=1),
		sidebar_link("Groom Profile", "DocType", "Groom Profile", child=1),
		sidebar_link("Horse Owner", "DocType", "Horse Owner", child=1),
		sidebar_section("Money"),
		sidebar_link("Financial Overview", "Report", "Financial Overview", child=1),
		sidebar_link("Money Flow Summary", "Report", "Money Flow Summary", child=1),
		sidebar_link("Spending By Category", "Report", "Spending By Category", child=1),
		sidebar_link("Financial Ledger", "Report", "Financial Ledger", child=1),
		sidebar_link("Transaction Input", "DocType", "Transaction Input", child=1),
		sidebar_link("Receipt Import", "DocType", "Receipt Import", child=1),
		sidebar_link("Purchase", "DocType", "Purchase", child=1),
		sidebar_link("Quote Comparison", "Report", "Quote Comparison", child=1),
		sidebar_link("Unposted Transactions", "Report", "Unposted Transactions", child=1),
		sidebar_link("Vendor Quote", "DocType", "Vendor Quote", child=1),
		sidebar_link("Vendor", "DocType", "Vendor", child=1),
		sidebar_link("Item", "DocType", "Item", child=1),
		sidebar_link("Item Category", "DocType", "Item Category", child=1),
		sidebar_link("Inventory Vendor Summary", "Report", "Inventory Vendor Summary", child=1),
		sidebar_link("Inventory Location", "DocType", "Inventory Location", child=1),
		sidebar_link("Stock Adjustment", "DocType", "Stock Adjustment", child=1),
		sidebar_link("Item Stock Ledger", "Report", "Item Stock Ledger", child=1),
		sidebar_link("Horse Expenses", "Report", "Horse Expenses", child=1),
		sidebar_link("Item Cost History", "Report", "Item Cost History", child=1),
		sidebar_link("Autopayments", "DocType", "Autopayments", child=1),
		sidebar_link("Money Account", "DocType", "Money Account", child=1),
		sidebar_section("Groom Work"),
		sidebar_url("Today Tasks", "/app/task/view/kanban/Whiteboard", icon="kanban", child=1),
		sidebar_link("Task List", "DocType", "Task", icon="list", child=1),
		sidebar_link("Horse Care Entry", "DocType", "Horse Care Entry", icon="clipboard-plus", child=1),
	]:
		sidebar.append("items", item)

	sidebar.save(ignore_permissions=True)


def setup_desktop_icon():
	icon = get_or_new("Desktop Icon", "Poloway")
	icon.label = "Poloway"
	icon.icon_type = "Link"
	icon.link_type = "Workspace Sidebar"
	icon.link_to = "Poloway"
	icon.sidebar = "Poloway"
	icon.icon = "flag"
	icon.parent_icon = ""
	icon.hidden = 0
	icon.restrict_removal = 0
	icon.standard = 1
	icon.app = "polomanagement"
	icon.roles = []
	for role in ["Horse Groom", "Horse Owner", "Stable Manager", "System Manager"]:
		icon.append("roles", {"role": role})
	icon.save(ignore_permissions=True)


def upsert_workspace(name, config):
	workspace = get_or_new("Workspace", name)
	workspace.label = name
	workspace.title = config["title"]
	workspace.module = "Polomanagement"
	workspace.app = "polomanagement"
	workspace.type = "Workspace"
	workspace.public = 1
	workspace.is_hidden = 0
	workspace.icon = config["icon"]
	workspace.indicator_color = config["indicator_color"]
	workspace.parent_page = config.get("parent_page")
	workspace.content = frappe.as_json(config["content"])
	workspace.shortcuts = []
	workspace.links = []
	workspace.number_cards = []
	workspace.charts = []
	workspace.roles = []

	for row in config["shortcuts"]:
		workspace.append("shortcuts", row)
	for row in config["links"]:
		workspace.append("links", row)
	for row in config.get("number_cards", []):
		workspace.append("number_cards", row)
	for row in config.get("charts", []):
		workspace.append("charts", row)
	for role in config["roles"]:
		workspace.append("roles", {"role": role})

	workspace.save(ignore_permissions=True)


def get_or_new(doctype, name):
	if frappe.db.exists(doctype, name):
		return frappe.get_doc(doctype, name)

	doc = frappe.new_doc(doctype)
	doc.name = name
	return doc


def task_whiteboard_shortcut():
	return shortcut(
		"Today Tasks",
		"DocType",
		"Task",
		doc_view="Kanban",
		kanban_board="Whiteboard",
		icon="kanban",
	)


def remove_owner_number_cards():
	for card_name in [
		"Open Issues",
		"Today Open Groom Tasks",
		"Today Completed Groom Tasks",
		"Upcoming Owner Tasks",
		"Horses Needing Attention",
	]:
		frappe.delete_doc_if_exists("Number Card", card_name, force=True)


def setup_dashboard_widgets():
	for card_name, report_name, report_field, color, background_color in [
		("Income", "Money Flow Summary", "income", "#2F9E44", "#EBFBEE"),
		("Outflow", "Money Flow Summary", "outflow", "#E03131", "#FFF5F5"),
		("Net Cash Flow", "Money Flow Summary", "net", "#1971C2", "#E7F5FF"),
		("Open Actions", "Owner Action Summary", "count", "#F08C00", "#FFF4E6"),
		("Open Issues", "Owner Action Summary", "issues", "#C92A2A", "#FFF5F5"),
		("Medical Due", "Horse Performance Summary", "medical_due", "#E67700", "#FFF4E6"),
		("Training Sessions", "Horse Performance Summary", "training_sessions", "#5C7CFA", "#EDF2FF"),
		("Stock Value", "Inventory Vendor Summary", "stock_value", "#087F5B", "#E6FCF5"),
		("Open Quotes", "Inventory Vendor Summary", "open_quotes", "#7048E8", "#F3F0FF"),
	]:
		upsert_report_number_card(card_name, report_name, report_field, color, background_color)

	for chart_name, report_name, chart_type in [
		("Money Flow", "Money Flow Summary", "Bar"),
		("Spending Breakdown", "Spending By Category", "Donut"),
		("Owner Actions", "Owner Action Summary", "Bar"),
		("Polo Performance", "Polo Performance Summary", "Donut"),
		("Horse Readiness", "Horse Performance Summary", "Bar"),
		("Inventory Value", "Inventory Vendor Summary", "Bar"),
	]:
		upsert_report_dashboard_chart(chart_name, report_name, chart_type)


def upsert_report_number_card(card_name, report_name, report_field, color, background_color):
	card_doc = get_or_new("Number Card", card_name)
	card_doc.label = card_name
	card_doc.type = "Report"
	card_doc.report_name = report_name
	card_doc.report_field = report_field
	card_doc.function = "Sum"
	card_doc.report_function = "Sum"
	card_doc.filters_json = frappe.as_json({})
	card_doc.dynamic_filters_json = frappe.as_json({})
	card_doc.is_public = 1
	card_doc.is_standard = 0
	card_doc.module = "Polomanagement"
	card_doc.color = color
	card_doc.background_color = background_color
	card_doc.show_full_number = 0
	card_doc.show_percentage_stats = 0
	card_doc.save(ignore_permissions=True)


def upsert_report_dashboard_chart(chart_name, report_name, chart_type):
	chart_doc = get_or_new("Dashboard Chart", chart_name)
	chart_doc.chart_name = chart_name
	chart_doc.chart_type = "Report"
	chart_doc.report_name = report_name
	chart_doc.use_report_chart = 1
	chart_doc.type = chart_type
	chart_doc.filters_json = frappe.as_json({})
	chart_doc.dynamic_filters_json = frappe.as_json({})
	chart_doc.custom_options = frappe.as_json({})
	chart_doc.is_public = 1
	chart_doc.is_standard = 0
	chart_doc.module = "Polomanagement"
	chart_doc.show_values_over_chart = 1 if chart_type == "Bar" else 0
	chart_doc.save(ignore_permissions=True)


def shortcut(label, shortcut_type, link_to, doc_view=None, kanban_board=None, icon=None):
	row = {
		"label": label,
		"type": shortcut_type,
		"link_to": link_to,
		"icon": icon,
	}
	if doc_view:
		row["doc_view"] = doc_view
	if kanban_board:
		row["kanban_board"] = kanban_board
	return row


def url_shortcut(label, url, icon=None):
	return {
		"label": label,
		"type": "URL",
		"url": url,
		"icon": icon,
	}


def number_card(name, label=None):
	return {
		"number_card_name": name,
		"label": label or name,
	}


def chart(name, label=None):
	return {
		"chart_name": name,
		"label": label or name,
	}


def card(label):
	return {
		"type": "Card Break",
		"label": label,
		"link_type": "DocType",
	}


def link(label, link_type, link_to=None):
	return {
		"type": "Link",
		"label": label,
		"link_type": link_type,
		"link_to": link_to or label,
	}


def content(block_type, name, col=4):
	key_map = {
		"shortcut": "shortcut_name",
		"card": "card_name",
		"number_card": "number_card_name",
		"chart": "chart_name",
	}
	key = key_map[block_type]
	return {
		"id": frappe.generate_hash(length=10),
		"type": block_type,
		"data": {
			key: name,
			"col": col,
		},
	}


def spacer():
	return {
		"id": frappe.generate_hash(length=10),
		"type": "spacer",
		"data": {"col": 12},
	}


def sidebar_link(label, link_type, link_to, icon=None, child=0):
	return {
		"type": "Link",
		"label": label,
		"link_type": link_type,
		"link_to": link_to,
		"icon": icon,
		"child": child,
	}


def sidebar_url(label, url, icon=None, child=0):
	return {
		"type": "Link",
		"label": label,
		"link_type": "URL",
		"url": url,
		"icon": icon,
		"child": child,
	}


def sidebar_section(label):
	return {
		"type": "Section Break",
		"label": label,
		"indent": 1,
		"collapsible": 1,
		"keep_closed": 0,
	}


def setup_inventory():
	setup_inventory_locations()
	setup_item_categories()
	migrate_legacy_inventory()


def setup_ledgers():
	setup_money_accounts()

	from polomanagement.polomanagement.payment_ledger import backfill_transaction_ledger_entries

	backfill_transaction_ledger_entries()


def setup_money_accounts():
	from polomanagement.polomanagement.payment_ledger import ensure_money_account

	for account_name, account_type, is_cash in [
		("Cash", "Asset", 1),
		("Bank", "Asset", 1),
		("Clearing", "Asset", 1),
	]:
		ensure_money_account(account_name, account_type, is_cash_account=is_cash)


def setup_money_reports():
	for report_name, ref_doctype in {
		"Financial Overview": "Transaction Input",
		"Money Flow Summary": "Transaction Input",
		"Spending By Category": "Transaction Input",
		"Horse Expenses": "Transaction Input",
		"Item Cost History": "Transaction Input",
		"Unposted Transactions": "Transaction Input",
		"Financial Ledger": "Payment Ledger Entry",
		"Owner Action Summary": "Owner Task",
		"Polo Performance Summary": "Match Day",
		"Horse Performance Summary": "Horse",
		"Inventory Vendor Summary": "Item",
	}.items():
		if frappe.db.exists("Report", report_name):
			frappe.db.set_value("Report", report_name, "ref_doctype", ref_doctype, update_modified=False)


def setup_inventory_locations():
	ensure_doc(
		"Inventory Location",
		"All Inventory Locations",
		{
			"location_name": "All Inventory Locations",
			"is_group": 1,
			"location_type": "Yard",
		},
	)
	for name, location_type in [
		("Feed Room", "Feed Room"),
		("Tack Room", "Tack Room"),
		("Medical Cabinet", "Store"),
		("Equipment Store", "Store"),
	]:
		ensure_doc(
			"Inventory Location",
			name,
			{
				"location_name": name,
				"parent_inventory_location": "All Inventory Locations",
				"location_type": location_type,
			},
		)


def setup_item_categories():
	ensure_doc(
		"Item Category",
		"All Item Categories",
		{
			"item_category_name": "All Item Categories",
			"is_group": 1,
			"category_type": "Other",
		},
	)
	for name, category_type, parent, location, unit, role, is_group in [
		("Food", "Food", "All Item Categories", "Feed Room", "kg", "Horse Groom", 1),
		("Supplements", "Supplement", "Food", "Feed Room", "unit", "Horse Groom", 0),
		("Medical", "Medical", "All Item Categories", "Medical Cabinet", "unit", "Veterinarian", 1),
		("Stable Supplies", "Stable Supply", "All Item Categories", "Equipment Store", "unit", "Stable Manager", 0),
		("Grooming Supplies", "Grooming", "All Item Categories", "Equipment Store", "unit", "Horse Groom", 1),
		("Horse Equipment", "Equipment", "All Item Categories", "Tack Room", "unit", "Stable Manager", 1),
		("Saddles", "Equipment", "Horse Equipment", "Tack Room", "unit", "Stable Manager", 0),
		("Bits", "Equipment", "Horse Equipment", "Tack Room", "unit", "Stable Manager", 0),
	]:
		ensure_doc(
			"Item Category",
			name,
			{
				"item_category_name": name,
				"parent_item_category": parent,
				"is_group": is_group,
				"category_type": category_type,
				"default_inventory_location": location,
				"default_unit": unit,
				"default_responsible_role": role,
			},
		)


def migrate_legacy_inventory():
	if frappe.db.table_exists("Horse Item Category"):
		for row in frappe.db.sql(
			"""
			select name, category_name, description
			from `tabHorse Item Category`
			""",
			as_dict=True,
		):
			name = row.category_name or row.name
			ensure_doc(
				"Item Category",
				name,
				{
					"item_category_name": name,
					"parent_item_category": "All Item Categories",
					"category_type": "Food" if name == "Food" else "Other",
					"description": row.description,
					"default_inventory_location": "Feed Room" if name == "Food" else None,
					"default_unit": "kg" if name == "Food" else None,
					"default_responsible_role": "Horse Groom" if name == "Food" else None,
				},
			)

	if not frappe.db.table_exists("Horse Feed Item"):
		return

	for row in frappe.db.sql(
		"""
		select name, item_name, category, default_unit, description, is_active
		from `tabHorse Feed Item`
		""",
		as_dict=True,
	):
		category = row.category or "Food"
		item_name = row.item_name or row.name
		if not frappe.db.exists("Item Category", category):
			ensure_doc(
				"Item Category",
				category,
				{
					"item_category_name": category,
					"parent_item_category": "All Item Categories",
					"category_type": "Food" if category == "Food" else "Other",
				},
			)

		item_docname = frappe.db.exists("Item", row.name) or frappe.db.get_value("Item", {"item_name": item_name}, "name") or row.name
		ensure_doc(
			"Item",
			item_docname,
			{
				"item_name": item_name,
				"item_category": category,
				"default_unit": row.default_unit,
				"description": row.description,
				"is_active": row.is_active,
				"legacy_category": category,
			},
		)
		update_legacy_item_links(row.name, item_docname)


def update_legacy_item_links(old_item, new_item):
	if old_item == new_item:
		return

	for doctype, fieldname in [
		("Horse Feeding Record", "item"),
		("Task", "feed_item"),
		("Task Template Item", "feed_item"),
		("Horse Care Entry", "feed_item"),
	]:
		if not frappe.db.table_exists(doctype):
			continue

		frappe.db.sql(
			f"update `tab{doctype}` set `{fieldname}` = %s where `{fieldname}` = %s",
			(new_item, old_item),
		)


def ensure_doc(doctype, name, values):
	if frappe.db.exists(doctype, name):
		doc = frappe.get_doc(doctype, name)
		is_new = False
	else:
		doc = frappe.new_doc(doctype)
		doc.name = name
		is_new = True

	for fieldname, value in values.items():
		if value is None:
			continue
		if is_new or not doc.get(fieldname):
			doc.set(fieldname, value)

	if is_new:
		doc.insert(ignore_permissions=True)
	else:
		doc.save(ignore_permissions=True)

	return doc
