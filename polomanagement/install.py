import frappe


POLOWAY_LOGO_URL = "/assets/polomanagement/images/Polowaylogo.jpeg"


def after_migrate():
	setup_task_kanban()
	setup_inventory()
	setup_ledgers()
	setup_money_reports()
	setup_horse_onboarding()
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
	setup_custom_dashboard_blocks()
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
				url_shortcut("Horse Management", "/app/horse-management-dashboard", icon="heart-handshake"),
				url_shortcut("Match Dashboard", "/app/match-dashboard", icon="trophy"),
				shortcut("Money Flow", "Report", "Money Flow Summary", icon="chart-column"),
				shortcut("Polo Performance", "Report", "Polo Performance Summary", icon="trophy"),
				shortcut("Upcoming Polo", "Report", "Upcoming Polo Schedule", icon="calendar-days"),
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
				number_card("Month Income"),
				number_card("Month Outflow"),
				number_card("Month Net Cash Flow"),
				number_card("YTD Net Cash Flow"),
				number_card("Upcoming Matches"),
				number_card("Open Actions"),
				number_card("Open Issues"),
				number_card("Medical Due"),
				number_card("Available Horses"),
				number_card("Horses Needing Attention"),
			],
			"charts": [
				chart("Money Flow"),
				chart("Spending Breakdown"),
				chart("Upcoming Polo"),
				chart("Polo Performance"),
				chart("Horse Readiness"),
			],
			"custom_blocks": [
				custom_block("Poloway Financial Snapshot"),
				custom_block("Poloway Upcoming Polo"),
				custom_block("Poloway Horse Performance"),
				custom_block("Poloway Owner Actions"),
				custom_block("Poloway Receipt Upload"),
			],
			"links": [
				card("Big Picture"),
				link("Money Flow Summary", "Report"),
				link("Spending By Category", "Report"),
				link("Financial Overview", "Report"),
				link("Upcoming Polo Schedule", "Report"),
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
				content("onboarding", "Poloway System Onboarding", col=12),
				content("number_card", "Income", col=2),
				content("number_card", "Outflow", col=2),
				content("number_card", "Net Cash Flow", col=2),
				content("number_card", "Open Actions", col=2),
				content("number_card", "Open Issues", col=2),
				content("number_card", "Medical Due", col=2),
				content("chart", "Money Flow", col=6),
				content("chart", "Spending Breakdown", col=6),
				content("chart", "Upcoming Polo", col=6),
				content("chart", "Polo Performance", col=6),
				content("chart", "Horse Readiness", col=6),
				spacer(),
				content("shortcut", "Owner Dashboard", col=3),
				content("shortcut", "Money Dashboard", col=3),
				content("shortcut", "Horse Management", col=3),
				content("shortcut", "Match Dashboard", col=3),
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
				shortcut("Upcoming Polo", "Report", "Upcoming Polo Schedule", icon="calendar-days"),
				shortcut("Polo Performance", "Report", "Polo Performance Summary", icon="trophy"),
				shortcut("Match Board", "Report", "Match Day Board", icon="columns-3"),
				shortcut("Travel", "DocType", "Travel Manifest", doc_view="List", icon="truck"),
				url_shortcut("Money Dashboard", "/app/money-dashboard", icon="circle-dollar-sign"),
				url_shortcut("Horse Management", "/app/horse-management-dashboard", icon="heart-handshake"),
				url_shortcut("Match Dashboard", "/app/match-dashboard", icon="trophy"),
			],
			"number_cards": [
				number_card("Open Actions"),
				number_card("Open Issues"),
				number_card("Medical Due"),
				number_card("Training Sessions"),
				number_card("Upcoming Matches"),
				number_card("Available Horses"),
				number_card("Horses Needing Attention"),
			],
			"charts": [
				chart("Owner Actions"),
				chart("Upcoming Polo"),
				chart("Horse Readiness"),
				chart("Polo Performance"),
			],
			"custom_blocks": [
				custom_block("Poloway Owner Actions"),
				custom_block("Poloway Upcoming Polo"),
				custom_block("Poloway Horse Performance"),
				custom_block("Poloway Receipt Upload"),
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
				link("Upcoming Polo Schedule", "Report"),
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
				content("onboarding", "Poloway System Onboarding", col=12),
				content("number_card", "Open Actions", col=3),
				content("number_card", "Open Issues", col=3),
				content("number_card", "Medical Due", col=3),
				content("number_card", "Training Sessions", col=3),
				content("chart", "Owner Actions", col=6),
				content("chart", "Upcoming Polo", col=6),
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
				content("shortcut", "Horse Management", col=3),
				content("shortcut", "Match Dashboard", col=3),
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
		"Horse Management Dashboard",
		{
			"title": "Horse Management Dashboard",
			"icon": "heart-handshake",
			"indicator_color": "blue",
			"parent_page": "Poloway",
			"roles": ["Horse Owner", "Stable Manager", "System Manager"],
			"shortcuts": [
				shortcut("Horses", "DocType", "Horse", doc_view="List", icon="heart-handshake"),
				shortcut("New Horse", "DocType", "Horse", doc_view="New", icon="plus"),
				shortcut("Horse Performance", "Report", "Horse Performance Summary", icon="activity"),
				shortcut("Compliance", "Report", "Horse Compliance Alerts", icon="shield-alert"),
				shortcut("Feeding Records", "Report", "Horse Feeding Records", icon="wheat"),
				shortcut("Training Records", "Report", "Horse Training Records", icon="dumbbell"),
				shortcut("Medical Records", "Report", "Horse Medical Records", icon="stethoscope"),
				shortcut("Horse Expenses", "Report", "Horse Expenses", icon="circle-dollar-sign"),
				shortcut("Training Templates", "DocType", "Horse Training Template", doc_view="List", icon="copy-check"),
				shortcut("Care Entry", "DocType", "Horse Care Entry", doc_view="New", icon="clipboard-plus"),
				shortcut("Grooms", "DocType", "Groom Profile", doc_view="List", icon="users"),
				shortcut("Owners", "DocType", "Horse Owner", doc_view="List", icon="user-round-check"),
			],
			"number_cards": [
				number_card("Available Horses"),
				number_card("Horses Needing Attention"),
				number_card("Medical Due"),
				number_card("Training Sessions"),
			],
			"charts": [
				chart("Horse Readiness"),
			],
			"custom_blocks": [
				custom_block("Poloway Horse Performance"),
			],
			"links": [
				card("Horse Profiles"),
				link("Horse", "DocType"),
				link("Horse Owner", "DocType"),
				card("Horse Records"),
				link("Horse Feeding Records", "Report"),
				link("Horse Training Records", "Report"),
				link("Horse Medical Records", "Report"),
				link("Horse Compliance Alerts", "Report"),
				card("Care Planning"),
				link("Horse Care Entry", "DocType"),
				link("Horse Training Template", "DocType"),
				link("Task Template", "DocType"),
				card("People and Costs"),
				link("Groom Profile", "DocType"),
				link("Horse Expenses", "Report"),
				link("Transaction Input", "DocType"),
			],
			"content": [
				content("number_card", "Available Horses", col=3),
				content("number_card", "Horses Needing Attention", col=3),
				content("number_card", "Medical Due", col=3),
				content("number_card", "Training Sessions", col=3),
				content("chart", "Horse Readiness", col=12),
				content("custom_block", "Poloway Horse Performance", col=12),
				spacer(),
				content("shortcut", "Horses", col=3),
				content("shortcut", "New Horse", col=3),
				content("shortcut", "Horse Performance", col=3),
				content("shortcut", "Compliance", col=3),
				content("shortcut", "Feeding Records", col=3),
				content("shortcut", "Training Records", col=3),
				content("shortcut", "Medical Records", col=3),
				content("shortcut", "Horse Expenses", col=3),
				content("shortcut", "Training Templates", col=3),
				content("shortcut", "Care Entry", col=3),
				content("shortcut", "Grooms", col=3),
				content("shortcut", "Owners", col=3),
				spacer(),
				content("card", "Horse Profiles", col=4),
				content("card", "Horse Records", col=4),
				content("card", "Care Planning", col=4),
				content("card", "People and Costs", col=4),
			],
		},
	)

	upsert_workspace(
		"Match Dashboard",
		{
			"title": "Match Dashboard",
			"icon": "trophy",
			"indicator_color": "orange",
			"parent_page": "Poloway",
			"roles": ["Horse Groom", "Horse Owner", "Stable Manager", "System Manager"],
			"shortcuts": [
				shortcut("Match Days", "DocType", "Match Day", doc_view="List", icon="flag"),
				shortcut("New Match Day", "DocType", "Match Day", doc_view="New", icon="plus"),
				shortcut("Upcoming Polo", "Report", "Upcoming Polo Schedule", icon="calendar-days"),
				shortcut("Polo Performance", "Report", "Polo Performance Summary", icon="trophy"),
				shortcut("Match Board", "Report", "Match Day Board", icon="columns-3"),
				shortcut("Travel", "DocType", "Travel Manifest", doc_view="List", icon="truck"),
				shortcut("Tack Config", "DocType", "Horse Tack Configuration", doc_view="List", icon="wrench"),
				shortcut("Owner Calendar", "DocType", "Owner Task", doc_view="Calendar", icon="calendar-days"),
				task_whiteboard_shortcut(),
			],
			"number_cards": [
				number_card("Upcoming Matches"),
			],
			"charts": [
				chart("Upcoming Polo"),
				chart("Polo Performance"),
			],
			"custom_blocks": [
				custom_block("Poloway Upcoming Polo"),
			],
			"links": [
				card("Match Planning"),
				link("Match Day", "DocType"),
				link("Upcoming Polo Schedule", "Report"),
				link("Polo Performance Summary", "Report"),
				link("Match Day Board", "Report"),
				card("Match Operations"),
				link("Travel Manifest", "DocType"),
				link("Horse Tack Configuration", "DocType"),
				link("Task", "DocType"),
				card("Owner Scheduling"),
				link("Owner Task", "DocType"),
				link("Owner Action Summary", "Report"),
			],
			"content": [
				content("number_card", "Upcoming Matches", col=3),
				content("chart", "Upcoming Polo", col=6),
				content("chart", "Polo Performance", col=6),
				content("custom_block", "Poloway Upcoming Polo", col=12),
				spacer(),
				content("shortcut", "Match Days", col=3),
				content("shortcut", "New Match Day", col=3),
				content("shortcut", "Upcoming Polo", col=3),
				content("shortcut", "Polo Performance", col=3),
				content("shortcut", "Match Board", col=3),
				content("shortcut", "Travel", col=3),
				content("shortcut", "Tack Config", col=3),
				content("shortcut", "Owner Calendar", col=3),
				content("shortcut", "Today Tasks", col=3),
				spacer(),
				content("card", "Match Planning", col=4),
				content("card", "Match Operations", col=4),
				content("card", "Owner Scheduling", col=4),
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
				url_shortcut("Upload Receipt", "/app/money-dashboard?upload_receipt=1", icon="receipt-text"),
				shortcut("New Transaction", "DocType", "Transaction Input", doc_view="New", icon="circle-dollar-sign"),
				shortcut("Ledger", "Report", "Financial Ledger", icon="book-open"),
				shortcut("New Item", "DocType", "Item", doc_view="New", icon="package-plus"),
				shortcut("New Purchase", "DocType", "Purchase", doc_view="New", icon="shopping-cart"),
				shortcut("Quote Comparison", "Report", "Quote Comparison", icon="scale"),
				shortcut("Autopayments", "DocType", "Autopayments", doc_view="List", icon="calendar-clock"),
			],
			"number_cards": [
				number_card("Income"),
				number_card("Outflow"),
				number_card("Net Cash Flow"),
				number_card("Month Income"),
				number_card("Month Outflow"),
				number_card("Month Net Cash Flow"),
				number_card("YTD Income"),
				number_card("YTD Outflow"),
				number_card("YTD Net Cash Flow"),
				number_card("Unposted Transactions"),
				number_card("Stock Value"),
				number_card("Open Quotes"),
			],
			"charts": [
				chart("Money Flow"),
				chart("Spending Breakdown"),
				chart("Inventory Value"),
			],
			"custom_blocks": [
				custom_block("Poloway Financial Snapshot"),
				custom_block("Poloway Money Operations"),
				custom_block("Poloway Receipt Upload"),
			],
			"links": [
				card("Buy and Pay"),
				link("Purchase", "DocType"),
				link("Transaction Input", "DocType"),
				link("Financial Ledger", "Report"),
				link("Unposted Transactions", "Report"),
				link("Money Flow Summary", "Report"),
				card("New Item and Quotes"),
				link("Item", "DocType"),
				link("Item Category", "DocType"),
				link("Vendor", "DocType"),
				link("Vendor Quote", "DocType"),
				link("Quote Comparison", "Report"),
				link("Inventory Vendor Summary", "Report"),
				card("Horse Feed and Stock"),
				link("Item", "DocType"),
				link("Item Category", "DocType"),
				link("Inventory Location", "DocType"),
				link("Stock Adjustment", "DocType"),
				link("Item Stock Ledger", "Report"),
				link("Horse Expenses", "Report"),
				card("Employees and Autopay"),
				link("Groom Profile", "DocType"),
				link("Autopayments", "DocType"),
				link("Transaction Input", "DocType"),
				link("Money Account", "DocType"),
				card("Receipts and Review"),
				link("Receipt Import", "DocType"),
				link("Financial Overview", "Report"),
				link("Spending By Category", "Report"),
				link("Item Cost History", "Report"),
			],
			"content": [
				content("number_card", "Income", col=2),
				content("number_card", "Outflow", col=2),
				content("number_card", "Net Cash Flow", col=2),
				content("number_card", "Unposted Transactions", col=2),
				content("number_card", "Stock Value", col=3),
				content("number_card", "Open Quotes", col=3),
				content("chart", "Money Flow", col=6),
				content("chart", "Spending Breakdown", col=6),
				content("chart", "Inventory Value", col=12),
				spacer(),
				content("shortcut", "Upload Receipt", col=3),
				content("shortcut", "New Transaction", col=3),
				content("shortcut", "Ledger", col=3),
				content("shortcut", "New Item", col=3),
				content("shortcut", "New Purchase", col=3),
				content("shortcut", "Quote Comparison", col=3),
				content("shortcut", "Autopayments", col=3),
				spacer(),
				content("card", "Buy and Pay", col=4),
				content("card", "New Item and Quotes", col=4),
				content("card", "Horse Feed and Stock", col=4),
				content("card", "Employees and Autopay", col=4),
				content("card", "Receipts and Review", col=4),
			],
			"replace_content_when_missing": ["Buy and Pay", "New Item and Quotes", "Horse Feed and Stock", "Employees and Autopay"],
			"replace_child_tables": ["shortcuts", "links"],
		},
	)


def setup_workspace_sidebar():
	sidebar = get_or_new("Workspace Sidebar", "Poloway")
	sidebar.title = "Poloway"
	sidebar.header_icon = "flag"
	sidebar.module = "Polomanagement"
	sidebar.app = "polomanagement"
	sidebar.module_onboarding = "Poloway System Onboarding"
	sidebar.standard = 1
	sidebar.items = []

	for item in [
		sidebar_link("Poloway Home", "Workspace", "Poloway", icon="home"),
		sidebar_link("Owner Dashboard", "Workspace", "Owner Dashboard", icon="layout-dashboard"),
		sidebar_link("Money Dashboard", "Workspace", "Money Dashboard", icon="circle-dollar-sign"),
		sidebar_link("Horse Management Dashboard", "Workspace", "Horse Management Dashboard", icon="heart-handshake"),
		sidebar_link("Match Dashboard", "Workspace", "Match Dashboard", icon="trophy"),
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
		sidebar_link("Upcoming Polo Schedule", "Report", "Upcoming Polo Schedule", child=1),
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
		sidebar_link("Horse Care Entry", "DocType", "Horse Care Entry", icon="clipboard-plus", child=1),
		sidebar_link("Horse Training Template", "DocType", "Horse Training Template", child=1),
		sidebar_section("Match Operations"),
		sidebar_link("Match Days", "DocType", "Match Day", icon="flag", child=1),
		sidebar_link("Upcoming Polo Schedule", "Report", "Upcoming Polo Schedule", child=1),
		sidebar_link("Polo Performance Summary", "Report", "Polo Performance Summary", child=1),
		sidebar_link("Match Day Board", "Report", "Match Day Board", child=1),
		sidebar_link("Travel Manifest", "DocType", "Travel Manifest", child=1),
		sidebar_link("Horse Tack Configuration", "DocType", "Horse Tack Configuration", child=1),
		sidebar_section("Money"),
		sidebar_link("Financial Overview", "Report", "Financial Overview", child=1),
		sidebar_link("Money Flow Summary", "Report", "Money Flow Summary", child=1),
		sidebar_link("Spending By Category", "Report", "Spending By Category", child=1),
		sidebar_link("Financial Ledger", "Report", "Financial Ledger", child=1),
		sidebar_link("Transaction Input", "DocType", "Transaction Input", child=1),
		sidebar_link("Receipt Import", "DocType", "Receipt Import", child=1),
		sidebar_link("Purchase", "DocType", "Purchase", child=1),
		sidebar_link("Vendor Quote", "DocType", "Vendor Quote", child=1),
		sidebar_link("Vendor", "DocType", "Vendor", child=1),
		sidebar_link("Item", "DocType", "Item", child=1),
		sidebar_link("Item Category", "DocType", "Item Category", child=1),
		sidebar_link("Inventory Location", "DocType", "Inventory Location", child=1),
		sidebar_link("Stock Adjustment", "DocType", "Stock Adjustment", child=1),
		sidebar_link("Employees / Grooms", "DocType", "Groom Profile", child=1),
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
	icon.icon = ""
	icon.logo_url = POLOWAY_LOGO_URL
	icon.icon_image = POLOWAY_LOGO_URL
	icon.parent_icon = ""
	icon.hidden = 0
	icon.restrict_removal = 0
	icon.standard = 1
	icon.app = "polomanagement"
	icon.roles = []
	for role in ["Horse Groom", "Horse Owner", "Stable Manager", "System Manager"]:
		icon.append("roles", {"role": role})
	icon.save(ignore_permissions=True)
	update_installed_app_desktop_icon()


def update_installed_app_desktop_icon():
	for name in frappe.get_all("Desktop Icon", filters={"app": "polomanagement"}, pluck="name"):
		icon = frappe.get_doc("Desktop Icon", name)
		icon.logo_url = POLOWAY_LOGO_URL
		icon.icon_image = POLOWAY_LOGO_URL
		if icon.icon == "flag":
			icon.icon = ""
		icon.save(ignore_permissions=True)


def upsert_workspace(name, config):
	workspace_exists = frappe.db.exists("Workspace", name)
	workspace = get_or_new("Workspace", name)
	workspace.label = name
	workspace.title = config["title"]
	workspace.module = None
	workspace.app = None
	workspace.type = "Workspace"
	workspace.public = 1
	workspace.is_hidden = 0
	workspace.icon = config["icon"]
	workspace.indicator_color = config["indicator_color"]
	workspace.parent_page = config.get("parent_page")

	if not workspace_exists or not workspace.content:
		workspace.content = frappe.as_json(config["content"])
	elif should_replace_workspace_content(workspace.content, config):
		workspace.content = frappe.as_json(config["content"])
	else:
		workspace.content = merge_workspace_content(workspace.content, config["content"])

	if name == "Poloway":
		remove_child_rows(
			workspace,
			"custom_blocks",
			lambda row: row.get("custom_block_name") == "Poloway Onboarding",
		)

	for table_field in config.get("replace_child_tables", []):
		workspace.set(table_field, [])

	merge_child_rows(workspace, "shortcuts", config["shortcuts"], shortcut_key)
	merge_child_rows(workspace, "links", config["links"], link_key)
	merge_child_rows(workspace, "number_cards", config.get("number_cards", []), number_card_key)
	merge_child_rows(workspace, "charts", config.get("charts", []), chart_key)
	merge_child_rows(workspace, "custom_blocks", config.get("custom_blocks", []), custom_block_key)
	merge_child_rows(workspace, "roles", [{"role": role} for role in config["roles"]], role_key)

	workspace.save(ignore_permissions=True)


def should_replace_workspace_content(existing_content, config):
	required_markers = config.get("replace_content_when_missing") or []
	if not required_markers:
		return False

	try:
		existing = frappe.parse_json(existing_content) or []
	except Exception:
		return True

	existing_names = {
		value
		for item in existing
		for value in (item.get("data") or {}).values()
		if isinstance(value, str)
	}
	return not any(marker in existing_names for marker in required_markers)


def merge_workspace_content(existing_content, required_content):
	try:
		existing = frappe.parse_json(existing_content) or []
	except Exception:
		existing = []

	existing = [
		item
		for item in existing
		if not (
			item.get("type") == "custom_block"
			and item.get("data", {}).get("custom_block_name") == "Poloway Onboarding"
		)
	]

	for row in required_content:
		if row.get("type") != "onboarding":
			continue

		required_name = row.get("data", {}).get("onboarding_name")
		if required_name != "Poloway System Onboarding":
			continue

		has_row = any(
			item.get("type") == "onboarding"
			and item.get("data", {}).get("onboarding_name") == required_name
			for item in existing
		)
		if not has_row:
			existing.append(row)

	return frappe.as_json(existing)


def remove_child_rows(doc, table_field, predicate):
	doc.set(table_field, [row for row in doc.get(table_field) if not predicate(row)])


def merge_child_rows(doc, table_field, rows, key_function):
	existing = {key_function(row) for row in doc.get(table_field)}
	for row in rows:
		key = key_function(row)
		if key in existing:
			continue
		doc.append(table_field, row)
		existing.add(key)


def shortcut_key(row):
	return row.get("label")


def link_key(row):
	return (row.get("type"), row.get("label"), row.get("link_type"), row.get("link_to"))


def number_card_key(row):
	return row.get("number_card_name")


def chart_key(row):
	return row.get("chart_name")


def custom_block_key(row):
	return row.get("custom_block_name")


def role_key(row):
	return row.get("role")


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
		("Income", "Money Flow Summary", "income", "#2F9E44", "#FFFFFF"),
		("Outflow", "Money Flow Summary", "outflow", "#C92A2A", "#FFFFFF"),
		("Net Cash Flow", "Money Flow Summary", "net", "#334155", "#FFFFFF"),
		("Open Actions", "Owner Action Summary", "count", "#B7791F", "#FFFFFF"),
		("Open Issues", "Owner Action Summary", "issues", "#C92A2A", "#FFFFFF"),
		("Medical Due", "Horse Performance Summary", "medical_due", "#B7791F", "#FFFFFF"),
		("Training Sessions", "Horse Performance Summary", "training_sessions", "#475569", "#FFFFFF"),
		("Stock Value", "Inventory Vendor Summary", "stock_value", "#2F9E44", "#FFFFFF"),
		("Open Quotes", "Inventory Vendor Summary", "open_quotes", "#B7791F", "#FFFFFF"),
	]:
		upsert_report_number_card(card_name, report_name, report_field, color, background_color)

	for card_name, method, document_type, color, background_color, label in [
		("Month Income", "polomanagement.owner_dashboard.month_income", "Transaction Input", "#2F9E44", "#FFFFFF", "Month Income"),
		("Month Outflow", "polomanagement.owner_dashboard.month_outflow", "Transaction Input", "#C92A2A", "#FFFFFF", "Month Outflow"),
		("Month Net Cash Flow", "polomanagement.owner_dashboard.month_net_cash_flow", "Transaction Input", "#334155", "#FFFFFF", "Month Net Cash Flow"),
		("YTD Income", "polomanagement.owner_dashboard.ytd_income", "Transaction Input", "#2F9E44", "#FFFFFF", "YTD Income"),
		("YTD Outflow", "polomanagement.owner_dashboard.ytd_outflow", "Transaction Input", "#C92A2A", "#FFFFFF", "YTD Outflow"),
		("YTD Net Cash Flow", "polomanagement.owner_dashboard.ytd_net_cash_flow", "Transaction Input", "#334155", "#FFFFFF", "YTD Net Cash Flow"),
		("Upcoming Matches", "polomanagement.owner_dashboard.upcoming_matches", "Match Day", "#334155", "#FFFFFF", "Upcoming Matches"),
		("Available Horses", "polomanagement.owner_dashboard.available_horses", "Horse", "#2F9E44", "#FFFFFF", "Available Horses"),
		("Horses Needing Attention", "polomanagement.owner_dashboard.horses_needing_attention", "Horse", "#B7791F", "#FFFFFF", "Horses Needing Attention"),
		("Unposted Transactions", "polomanagement.owner_dashboard.unposted_transactions", "Transaction Input", "#B7791F", "#FFFFFF", "Unposted Transactions"),
	]:
		upsert_custom_number_card(card_name, method, document_type, color, background_color, label)

	for chart_name, report_name, chart_type, colors in [
		("Money Flow", "Money Flow Summary", "Bar", ["#2F9E44", "#C92A2A"]),
		("Spending Breakdown", "Spending By Category", "Bar", ["#C92A2A"]),
		("Owner Actions", "Owner Action Summary", "Bar", ["#B7791F", "#2F9E44", "#C92A2A"]),
		("Upcoming Polo", "Upcoming Polo Schedule", "Bar", ["#C9A227", "#64748B", "#94A3B8"]),
		("Polo Performance", "Polo Performance Summary", "Bar", ["#C9A227", "#64748B", "#94A3B8"]),
		("Horse Readiness", "Horse Performance Summary", "Bar", ["#C9A227"]),
		("Inventory Value", "Inventory Vendor Summary", "Bar", ["#2F9E44"]),
	]:
		upsert_report_dashboard_chart(chart_name, report_name, chart_type, colors)


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


def upsert_custom_number_card(card_name, method, document_type, color, background_color, label=None):
	card_doc = get_or_new("Number Card", card_name)
	card_doc.label = label or card_name
	card_doc.type = "Custom"
	card_doc.method = method
	card_doc.report_name = None
	card_doc.report_field = None
	card_doc.document_type = document_type
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


def upsert_report_dashboard_chart(chart_name, report_name, chart_type, colors=None):
	chart_doc = get_or_new("Dashboard Chart", chart_name)
	chart_doc.chart_name = chart_name
	chart_doc.chart_type = "Report"
	chart_doc.report_name = report_name
	chart_doc.use_report_chart = 1
	chart_doc.type = chart_type
	chart_doc.filters_json = frappe.as_json({})
	chart_doc.dynamic_filters_json = frappe.as_json({})
	chart_doc.custom_options = frappe.as_json({"colors": colors or []})
	chart_doc.is_public = 1
	chart_doc.is_standard = 0
	chart_doc.module = "Polomanagement"
	chart_doc.show_values_over_chart = 1 if chart_type == "Bar" else 0
	chart_doc.save(ignore_permissions=True)


def setup_custom_dashboard_blocks():
	roles = ["Horse Owner", "Stable Manager", "System Manager"]
	for block_name, html, style, script in [
		(
			"Poloway Financial Snapshot",
			'<div class="pm-block" data-block="financial"><div class="pm-muted">Loading financial snapshot...</div></div>',
			dashboard_block_style(),
			financial_snapshot_script(),
		),
		(
			"Poloway Upcoming Polo",
			'<div class="pm-block" data-block="polo"><div class="pm-muted">Loading upcoming polo...</div></div>',
			dashboard_block_style(),
			upcoming_polo_script(),
		),
		(
			"Poloway Horse Performance",
			'<div class="pm-block" data-block="horses"><div class="pm-muted">Loading horse performance...</div></div>',
			dashboard_block_style(),
			horse_performance_script(),
		),
		(
			"Poloway Owner Actions",
			'<div class="pm-block" data-block="actions"><div class="pm-muted">Loading owner actions...</div></div>',
			dashboard_block_style(),
			owner_actions_script(),
		),
		(
			"Poloway Money Operations",
			'<div class="pm-block" data-block="money-operations"><div class="pm-muted">Loading money operations...</div></div>',
			dashboard_block_style(),
			money_operations_script(),
		),
		(
			"Poloway Receipt Upload",
			'<div class="pm-block" data-block="receipt-upload"><h3>Receipt Upload</h3><p>Upload receipt images and let Poloway create the transaction input.</p><button class="pm-button" type="button">Upload Receipt</button></div>',
			dashboard_block_style(),
			receipt_upload_script(),
		),
	]:
		upsert_custom_html_block(block_name, html, style, script, roles)
	frappe.delete_doc_if_exists("Custom HTML Block", "Poloway Onboarding", force=True)


def upsert_custom_html_block(name, html, style, script, roles):
	block = get_or_new("Custom HTML Block", name)
	block.html = html
	block.style = style
	block.script = script
	block.private = 0
	block.roles = []
	for role in roles:
		block.append("roles", {"role": role})
	block.save(ignore_permissions=True)


def dashboard_block_style():
	return """
.pm-block {
	font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
	color: var(--text-color, #1f272e);
	background: var(--card-bg, #ffffff);
	border: 1px solid var(--border-color, #d1d8dd);
	border-radius: 8px;
	box-shadow: none;
	padding: 16px;
	min-height: 100%;
}
.pm-block h3 {
	margin: 0 0 12px;
	font-size: 15px;
	font-weight: 750;
	letter-spacing: 0;
	color: var(--heading-color, #1f272e);
}
.pm-block p {
	margin: 0 0 12px;
	color: var(--text-muted, #6b7280);
	font-size: 13px;
	line-height: 1.45;
}
.pm-muted,
.pm-empty {
	color: var(--text-muted, #6b7280);
	font-size: 13px;
	padding: 8px 0;
}
.pm-metrics {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(118px, 1fr));
	gap: 8px;
	margin-bottom: 14px;
}
.pm-metric {
	border: 1px solid var(--border-color, #d1d8dd);
	border-radius: 7px;
	padding: 10px 11px;
	background: var(--card-bg, #ffffff);
}
.pm-value {
	display: block;
	font-size: 18px;
	font-weight: 760;
	color: var(--text-color, #1f272e);
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}
.pm-label,
.pm-meta {
	display: block;
	font-size: 12px;
	color: var(--text-muted, #6b7280);
	line-height: 1.35;
}
.pm-tone-positive .pm-value {
	color: #2f9e44;
}
.pm-tone-negative .pm-value {
	color: #c92a2a;
}
.pm-tone-warning .pm-value {
	color: #b7791f;
}
.pm-tone-accent .pm-value {
	color: var(--text-color, #1f272e);
}
.pm-list {
	display: grid;
	gap: 6px;
}
.pm-row {
	display: block;
	border: 1px solid var(--border-color, #d1d8dd);
	border-radius: 7px;
	padding: 9px 10px;
	color: inherit;
	text-decoration: none;
	background: var(--card-bg, #ffffff);
}
.pm-row:hover {
	background: var(--control-bg, #f3f3f3);
	border-color: var(--border-color, #d1d8dd);
	text-decoration: none;
}
.pm-title {
	display: block;
	font-weight: 650;
	font-size: 13px;
	color: var(--text-color, #1f272e);
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}
.pm-next {
	display: block;
	border: 1px solid var(--border-color, #d1d8dd);
	border-radius: 8px;
	background: var(--card-bg, #ffffff);
	padding: 11px;
	margin-bottom: 10px;
	color: inherit;
	text-decoration: none;
}
.pm-next:hover {
	background: var(--control-bg, #f3f3f3);
	text-decoration: none;
}
.pm-button {
	border: 1px solid #2e2413;
	border-radius: 7px;
	background: #2e2413;
	color: #ffffff;
	font-weight: 650;
	padding: 8px 12px;
	cursor: pointer;
	box-shadow: none;
}
.pm-button:hover {
	background: #443315;
	border-color: #443315;
}
"""


def shared_block_script_helpers():
	return """
const root = root_element;
const esc = (value) => {
	const div = document.createElement("div");
	div.innerText = value == null ? "" : String(value);
	return div.innerHTML;
};
const toNumber = (value) => {
	const number = Number(value);
	return Number.isFinite(number) ? number : 0;
};
const money = (value) => {
	const number = toNumber(value);
	if (typeof format_currency === "function") {
		const formatted = format_currency(number);
		if (formatted && !String(formatted).includes("NaN")) {
			return formatted;
		}
	}
	const currency = (frappe.boot && frappe.boot.sysdefaults && frappe.boot.sysdefaults.currency) || "ZAR";
	return new Intl.NumberFormat(undefined, {
		style: "currency",
		currency,
		maximumFractionDigits: 0,
	}).format(number);
};
const dateLabel = (value) => value && frappe.datetime ? frappe.datetime.str_to_user(value) : (value || "");
const metric = (label, value, tone) => `<div class="pm-metric pm-tone-${esc(tone || "neutral")}"><span class="pm-value">${esc(value)}</span><span class="pm-label">${esc(label)}</span></div>`;
const row = (label, meta, route) => `<a class="pm-row" href="#" data-route='${JSON.stringify(route || [])}'><span class="pm-title">${esc(label)}</span><span class="pm-meta">${esc(meta || "")}</span></a>`;
const renderBlock = (html) => {
	const container = root.querySelector(".pm-block");
	if (container) {
		container.outerHTML = html;
	} else {
		root.insertAdjacentHTML("afterbegin", html);
	}
};
const bindRoutes = () => {
	root.querySelectorAll("[data-route]").forEach((item) => {
		item.addEventListener("click", (event) => {
			event.preventDefault();
			const route = JSON.parse(item.getAttribute("data-route") || "[]");
			if (route.length) {
				frappe.set_route(...route);
			}
		});
	});
};
"""


def financial_snapshot_script():
	return shared_block_script_helpers() + """
frappe.call({
	method: "polomanagement.owner_dashboard.get_financial_dashboard_component",
	callback(r) {
		const data = r.message || {};
		const month = data.month || {};
		const year = data.year || {};
		const recent = data.recent || [];
		renderBlock(`
			<div class="pm-block">
				<h3>Financial Snapshot</h3>
				<div class="pm-metrics">
					${metric("Month Income", money(month.income), "positive")}
					${metric("Month Outflow", money(month.outflow), "negative")}
					${metric("Month Net", money(month.net), toNumber(month.net) >= 0 ? "positive" : "negative")}
					${metric("YTD Net", money(year.net), toNumber(year.net) >= 0 ? "positive" : "negative")}
				</div>
				<div class="pm-list">
					${recent.length ? recent.map((item) => row(
						[item.transaction_category || item.transaction_type, money(item.total_amount)].filter(Boolean).join(" / "),
						[dateLabel(item.transaction_date), item.direction].filter(Boolean).join(" / "),
						["Form", "Transaction Input", item.name]
					)).join("") : `<div class="pm-empty">No posted transactions yet.</div>`}
				</div>
			</div>
		`);
		bindRoutes();
	},
});
"""


def upcoming_polo_script():
	return shared_block_script_helpers() + """
frappe.call({
	method: "polomanagement.owner_dashboard.get_polo_dashboard_component",
	callback(r) {
		const data = r.message || {};
		const next = data.next_match;
		const upcoming = data.upcoming || [];
		renderBlock(`
			<div class="pm-block">
				<h3>Upcoming Polo</h3>
				${next ? `<a class="pm-next" href="#" data-route='${JSON.stringify(["Form", "Match Day", next.name])}'>
					<span class="pm-title">${esc(next.event_name || next.name)}</span>
					<span class="pm-meta">${esc([dateLabel(next.match_date), next.venue, next.status].filter(Boolean).join(" / "))}</span>
					<span class="pm-meta">${esc([next.team, next.opponent].filter(Boolean).join(" vs "))}</span>
				</a>` : `<div class="pm-empty">No upcoming match day has been scheduled.</div>`}
				<div class="pm-list">
					${upcoming.length ? upcoming.map((item) => row(
						item.event_name || item.name,
						[dateLabel(item.match_date), item.venue, item.status].filter(Boolean).join(" / "),
						["Form", "Match Day", item.name]
					)).join("") : ""}
				</div>
			</div>
		`);
		bindRoutes();
	},
});
"""


def horse_performance_script():
	return shared_block_script_helpers() + """
frappe.call({
	method: "polomanagement.owner_dashboard.get_horse_dashboard_component",
	callback(r) {
		const data = r.message || {};
		const counts = data.counts || {};
		const top = data.top_training || [];
		renderBlock(`
			<div class="pm-block">
				<h3>Horse Performance</h3>
				<div class="pm-metrics">
					${metric("Horses", counts.total || 0, "accent")}
					${metric("Available", counts.available || 0, "positive")}
					${metric("Need Attention", counts.attention || 0, counts.attention ? "warning" : "positive")}
					${metric("Training 30d", counts.training_30d || 0, "accent")}
				</div>
				<div class="pm-list">
					${top.length ? top.map((item) => row(
						item.horse_name || item.horse,
						[`Completed ${item.completed || 0}`, `Follow up ${item.follow_up || 0}`].join(" / "),
						["Form", "Horse", item.horse]
					)).join("") : `<div class="pm-empty">No training performance yet.</div>`}
				</div>
			</div>
		`);
		bindRoutes();
	},
});
"""


def owner_actions_script():
	return shared_block_script_helpers() + """
frappe.call({
	method: "polomanagement.owner_dashboard.get_owner_actions_dashboard_component",
	callback(r) {
		const data = r.message || {};
		const groom = data.groom_today || {};
		const tasks = data.open_tasks || [];
		const issues = data.open_issues || [];
		renderBlock(`
			<div class="pm-block">
				<h3>Owner Actions</h3>
				<div class="pm-metrics">
					${metric("Groom Open", groom.open || 0, groom.open ? "warning" : "positive")}
					${metric("Groom Completed", groom.completed || 0, "positive")}
					${metric("Open Issues", issues.length || 0, issues.length ? "negative" : "positive")}
				</div>
				<div class="pm-list">
					${tasks.length ? tasks.map((item) => row(
						item.subject || item.name,
						[dateLabel(item.due_date), item.priority, item.task_type].filter(Boolean).join(" / "),
						["Form", "Owner Task", item.name]
					)).join("") : `<div class="pm-empty">No open owner tasks.</div>`}
				</div>
			</div>
		`);
		bindRoutes();
	},
});
"""


def money_operations_script():
	return shared_block_script_helpers() + """
frappe.call({
	method: "polomanagement.owner_dashboard.get_money_operations_dashboard_component",
	callback(r) {
		const data = r.message || {};
		const financial = data.financial || {};
		const operations = data.operations || {};
		const inventory = data.inventory || {};
		const vendors = data.vendors || {};
		renderBlock(`
			<div class="pm-block">
				<h3>Money Operations</h3>
				<div class="pm-metrics">
					${metric("Unposted", financial.unposted || 0, financial.unposted ? "warning" : "positive")}
					${metric("Open Purchases", financial.open_purchases || 0, financial.open_purchases ? "warning" : "positive")}
					${metric("Items", inventory.items || 0, "accent")}
					${metric("Vendors", vendors.vendors || 0, "accent")}
				</div>
				<div class="pm-list">
					${(operations.purchases || []).length ? operations.purchases.map((item) => row(
						item.purchase_title || item.name,
						[item.status, dateLabel(item.needed_by), money(item.estimated_total)].filter(Boolean).join(" / "),
						["Form", "Purchase", item.name]
					)).join("") : `<div class="pm-empty">No open purchases.</div>`}
				</div>
			</div>
		`);
		bindRoutes();
	},
});
"""


def receipt_upload_script():
	return """
root_element.querySelector("button").addEventListener("click", () => {
	if (window.polomanagement_upload_receipts) {
		window.polomanagement_upload_receipts({});
	} else {
		frappe.new_doc("Receipt Import");
	}
});
"""


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


def custom_block(name, label=None):
	return {
		"custom_block_name": name,
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
		"onboarding": "onboarding_name",
		"custom_block": "custom_block_name",
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
		"Upcoming Polo Schedule": "Match Day",
		"Polo Performance Summary": "Match Day",
		"Horse Performance Summary": "Horse",
		"Inventory Vendor Summary": "Item",
	}.items():
		if frappe.db.exists("Report", report_name):
			frappe.db.set_value("Report", report_name, "ref_doctype", ref_doctype, update_modified=False)


def setup_horse_onboarding():
	frappe.db.set_single_value("System Settings", "enable_onboarding", 1)
	frappe.delete_doc_if_exists("Module Onboarding", "Horse System Onboarding", force=True)

	setup_poloway_form_tours()

	upsert_module_onboarding(
		"Poloway System Onboarding",
		"Poloway Setup",
		["Horse Owner", "Stable Manager", "System Manager"],
		[
			upsert_onboarding_step(
				"Create the first horse profile",
				"Create Entry",
				"Create a complete horse profile. This starts the Horse Profile Basics form tour and walks through name, registration, location, handling, playing, availability, ownership, and linked records.",
				reference_document="Horse",
				action_label="Create Horse",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Horse Profile Basics",
			),
			upsert_onboarding_step(
				"Tour feeding records",
				"Show Form Tour",
				"Learn how feeding records link one horse, one food item, quantity, timing, responsible person, and notes.",
				reference_document="Horse Feeding Record",
				action_label="Start Feeding Tour",
				form_tour="Horse Feeding Record Basics",
			),
			upsert_onboarding_step(
				"Tour training records",
				"Show Form Tour",
				"Learn how training records capture templates, work type, duration, intensity, outcome, ratings, and notes.",
				reference_document="Horse Training Record",
				action_label="Start Training Tour",
				form_tour="Horse Training Record Basics",
			),
			upsert_onboarding_step(
				"Tour medical records",
				"Show Form Tour",
				"Learn how medical records capture all medical events and link them to the responsible person, not only a veterinarian.",
				reference_document="Horse Medical Record",
				action_label="Start Medical Tour",
				form_tour="Horse Medical Record Basics",
			),
			upsert_onboarding_step(
				"Review horse performance",
				"View Report",
				"Open the horse performance report to see training, chukkers, issues, medical due items, expenses, and readiness score by horse.",
				reference_report="Horse Performance Summary",
				action_label="View Horse Performance",
				report_description="This is the owner-facing summary for horse performance and care attention.",
			),
			upsert_onboarding_step(
				"Review medical follow-ups",
				"View Report",
				"Open the horse compliance report to see medical records with upcoming or overdue next due dates.",
				reference_report="Horse Compliance Alerts",
				action_label="View Compliance",
				report_description="Use this to catch medical follow-ups before they are missed.",
			),
			upsert_onboarding_step(
				"Create inventory items",
				"Create Entry",
				"Create feed, tack, medicine, supplies, services, and other items before using them in feeding, receipts, and financial entries.",
				reference_document="Item",
				action_label="Create Item",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Item Basics",
			),
			upsert_onboarding_step(
				"Create vendors",
				"Create Entry",
				"Create suppliers, vets, farriers, transport providers, horse sellers, buyers, and service providers for purchases and receipts.",
				reference_document="Vendor",
				action_label="Create Vendor",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Vendor Basics",
			),
			upsert_onboarding_step(
				"Create the groom task template",
				"Create Entry",
				"Build the daily task template that generates the groom's work list.",
				reference_document="Task Template",
				action_label="Create Task Template",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Task Template Basics",
			),
			upsert_onboarding_step(
				"Configure task generation",
				"Show Form Tour",
				"Set the default template, default groom, days ahead, and day-specific overrides.",
				reference_document="Task Schedule Settings",
				action_label="Configure Scheduling",
				form_tour="Task Schedule Settings Basics",
			),
			upsert_onboarding_step(
				"Open the groom task board",
				"Go to Page",
				"Open the kanban task board to see how generated tasks appear for the groom.",
				action_label="Open Task Board",
				path="/app/task/view/kanban/Whiteboard",
				callback_title="Groom task board",
				callback_message="This board is the groom's day view. Moving a task to completed triggers the completion flow.",
			),
			upsert_onboarding_step(
				"Create a manual transaction",
				"Create Entry",
				"Use Transaction Input as the one central place to create ledger entries manually.",
				reference_document="Transaction Input",
				action_label="Create Transaction",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Transaction Input Basics",
			),
			upsert_onboarding_step(
				"Review money flow",
				"View Report",
				"Open the money flow report to understand income, outflow, and net cash flow.",
				reference_report="Money Flow Summary",
				action_label="View Money Flow",
				report_description="This report powers the owner money dashboard and shows the big financial picture.",
			),
			upsert_onboarding_step(
				"Upload receipts",
				"Create Entry",
				"Upload one or more receipts so OCR and AI can extract details, match items and vendors, and create transaction input records.",
				reference_document="Receipt Import",
				action_label="Upload Receipt",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Receipt Upload Basics",
			),
			upsert_onboarding_step(
				"Review the ledger",
				"View Report",
				"Open the financial ledger after transactions and receipt imports have posted.",
				reference_report="Financial Ledger",
				action_label="View Ledger",
				report_description="This is the immutable ledger view for posted financial movement.",
			),
		],
	)


def setup_poloway_form_tours():
	for title, doctype, steps in [
		(
			"Horse Profile Basics",
			"Horse",
			[
				("name1", "Horse name", "This is the everyday stable name used when people link horses."),
				("height", "Height and weight", "Height is recorded in metres and weight is recorded in kilograms."),
				("registration_number", "Registration", "Use registration for passport, microchip, registered name, and authority details."),
				("current_location", "Location", "Track where the horse is kept now, including stable number and location notes."),
				("temperament", "Handling", "Record handling notes and special instructions for grooms, vets, and farriers."),
				("playing_status", "Playing information", "Track playing status, position, handicap, and playing notes."),
				("availability_status", "Availability", "Show whether the horse is available, reserved, unavailable, sold, or leased."),
				("ownership", "Ownership", "Ownership stays on the horse profile and should be restricted to owner and management roles."),
				("medical_records_report", "Linked records", "Use these buttons to open filtered reports for feeding, training, and medical history."),
			],
		),
		(
			"Horse Feeding Record Basics",
			"Horse Feeding Record",
			[
				("horse", "Choose the horse", "Every feeding entry must point to the horse it applies to."),
				("feeding_date", "Date and time", "Record when feeding happened so daily care history stays accurate."),
				("item", "Food item", "Only food items should be selected here. Quantity belongs on this record."),
				("quantity", "Quantity", "Record the actual amount given and the unit used."),
				("notes", "Notes", "Use notes for refusals, appetite changes, substitutions, or anything the owner should review."),
			],
		),
		(
			"Horse Training Record Basics",
			"Horse Training Record",
			[
				("horse", "Choose the horse", "Every training record belongs to one horse."),
				("training_template", "Training template", "Use a template when the work follows a planned routine."),
				("work_type", "Work type", "Select the work done, then record duration and intensity."),
				("outcome", "Outcome", "Use Needs Follow Up when something should be checked later."),
				("speed_rating", "Performance notes", "Ratings help owners see patterns across sessions."),
				("notes", "Notes", "Add short practical notes about how the session went."),
			],
		),
		(
			"Horse Medical Record Basics",
			"Horse Medical Record",
			[
				("horse", "Choose the horse", "Every medical record must link to the horse."),
				("record_type", "Record type", "Use this for checkups, vaccinations, injuries, treatment, medication, farrier, dental, and observations."),
				("responsible_person", "Responsible person", "This is the person responsible for the event. It does not have to be a veterinarian."),
				("summary", "Summary", "Write the short version here so dashboards and reports are readable."),
				("medication_or_materials", "Materials and dosage", "Record medication, materials, dosage, or quantity when anything was used."),
				("next_due_date", "Next due date", "Set follow-up care, boosters, monitoring, or appointment dates here."),
				("notes", "Notes", "Use notes for detailed observations or instructions."),
			],
		),
		(
			"Item Basics",
			"Item",
			[
				("item_name", "Item name", "Create anything you buy, stock, feed, sell, or assign cost to."),
				("item_category", "Category", "Categories drive filtering and defaults. Food items should sit under food categories."),
				("is_stock_item", "Stock item", "Enable this for feed, tack, supplies, medicine, and anything with quantity on hand."),
				("inventory_location", "Location", "Choose where this item lives, such as feed room, tack room, or medical cabinet."),
				("quantity_on_hand", "Quantity and value", "Set quantity, unit, cost per item, and total value."),
				("responsible_role", "Responsibility", "Use assignment fields when a role or user is responsible for the item."),
			],
		),
		(
			"Vendor Basics",
			"Vendor",
			[
				("vendor_name", "Vendor name", "Create suppliers, vets, farriers, transport providers, horse sellers, buyers, and service providers here."),
				("vendor_type", "Vendor type", "Type separates feed suppliers, tack suppliers, vets, farriers, transport, and tournament vendors."),
				("contact_person", "Contact", "Keep contact information here so purchases and quotes have a clear source."),
				("default_currency", "Commercial defaults", "Set default currency and payment terms when known."),
				("notes", "Notes", "Use notes for commercial context or owner comments."),
			],
		),
		(
			"Task Template Basics",
			"Task Template",
			[
				("template_name", "Template name", "Create a repeatable daily routine such as Regular Stable Day or Tournament Morning."),
				("is_active", "Active template", "Only active templates should be used for automatic task generation."),
				("description", "Description", "Explain what this template is for."),
				("items", "Task items", "Add groom tasks here: feeding, training, medical, or general work, with horse, time, assignee, and instructions."),
			],
		),
		(
			"Task Schedule Settings Basics",
			"Task Schedule Settings",
			[
				("enabled", "Auto generate", "Turn this on when Poloway should generate groom tasks automatically."),
				("default_template", "Default template", "Choose the normal template for future days."),
				("default_assigned_to", "Default groom", "Set the default groom user who receives generated tasks."),
				("days_ahead", "Days ahead", "Control how far ahead tasks should be created."),
				("overrides", "Overrides", "Use overrides for days needing a different template or assignment."),
			],
		),
		(
			"Transaction Input Basics",
			"Transaction Input",
			[
				("transaction_type", "Transaction type", "All money entry starts here: purchase, sale, expense, or income."),
				("transaction_category", "Category and direction", "Category explains what the money is for; direction decides money in or money out."),
				("transaction_date", "Date", "Use the actual transaction date from the source document or receipt."),
				("party_type", "Party", "Choose whether this relates to a vendor, owner, groom, customer, tournament organizer, or other party."),
				("payment_method", "Payment", "Capture method, account, currency, and total amount."),
				("lines", "Transaction entries", "Add entries for items, horses, grooms, tournaments, services, or other costs."),
				("notes", "Notes", "Use notes for context that should remain with the financial record."),
			],
		),
		(
			"Receipt Upload Basics",
			"Receipt Import",
			[
				("receipt_attachment", "Single receipt", "Attach one receipt image here when processing one file."),
				("receipt_files", "Multiple receipts", "Use the child table when uploading multiple receipt images at once."),
				("post_payment_immediately", "Posting choice", "Enable this only when imported transactions should be submitted immediately after processing."),
				("linked_horse", "Horse context", "Link a horse when the receipt clearly belongs to a specific horse."),
				("vendor", "Matched vendor", "Review the matched vendor before posting."),
				("total_amount", "Parsed totals", "Review date, category, payment method, currency, confidence, and total amount before applying."),
				("lines", "Extracted lines", "Review item, horse, groom, tournament, quantity, rate, tax, and category matches."),
				("transaction_input", "Transaction input", "After processing, this links to the central transaction that creates ledger entries."),
			],
		),
	]:
		upsert_form_tour(title, doctype, steps)


def upsert_module_onboarding(name, title, roles, steps):
	onboarding = get_or_new("Module Onboarding", name)
	onboarding.title = title
	onboarding.module = "Polomanagement"
	onboarding.is_complete = 0
	onboarding.allow_roles = []
	for role in roles:
		onboarding.append("allow_roles", {"role": role})
	onboarding.steps = []
	for step in steps:
		onboarding.append("steps", {"step": step})
	onboarding.save(ignore_permissions=True)


def upsert_onboarding_step(
	title,
	action,
	description,
	reference_document=None,
	reference_report=None,
	action_label=None,
	show_full_form=0,
	show_form_tour=0,
	form_tour=None,
	report_description=None,
	path=None,
	callback_title=None,
	callback_message=None,
):
	step = get_or_new("Onboarding Step", title)
	step.title = title
	step.action = action
	step.description = description
	step.action_label = action_label or title
	step.reference_document = reference_document
	step.reference_report = reference_report
	step.show_full_form = show_full_form
	step.show_form_tour = show_form_tour
	step.form_tour = form_tour
	step.report_description = report_description
	step.path = path
	step.callback_title = callback_title
	step.callback_message = callback_message
	step.is_complete = 0
	step.is_skipped = 0
	step.save(ignore_permissions=True)
	return step.name


def upsert_form_tour(title, reference_doctype, steps):
	tour = get_or_new("Form Tour", title)
	tour.title = title
	tour.reference_doctype = reference_doctype
	tour.ui_tour = 0
	tour.is_standard = 0
	tour.save_on_complete = 0
	tour.first_document = 1
	tour.include_name_field = 0
	tour.steps = []
	for fieldname, step_title, description in steps:
		tour.append(
			"steps",
			{
				"fieldname": fieldname,
				"title": step_title,
				"description": f"<p>{description}</p>",
				"position": "Bottom",
			},
		)
	tour.save(ignore_permissions=True)


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
