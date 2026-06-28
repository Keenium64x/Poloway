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
			"dashboard_onboarding": "Poloway System Onboarding",
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
			"dashboard_onboarding": "Groom Dashboard Onboarding",
			"replace_onboardings": ["Poloway System Onboarding"],
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
				content("onboarding", "Groom Dashboard Onboarding", col=12),
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
			"dashboard_onboarding": "Owner Dashboard Onboarding",
			"replace_onboardings": ["Poloway System Onboarding"],
			"roles": ["Horse Owner", "Stable Manager", "System Manager"],
			"shortcuts": [
				shortcut("Owner Actions", "Report", "Owner Action Summary", icon="list-checks"),
				shortcut("New Owner Action", "DocType", "Owner Task", doc_view="New", icon="plus"),
				task_whiteboard_shortcut(),
				shortcut("Owner Calendar", "DocType", "Owner Task", doc_view="Calendar", icon="calendar-days"),
				url_shortcut("Owner Gantt", "/app/owner-task/view/gantt", icon="gantt-chart"),
				shortcut("Issues", "Report", "Owner Task Issues", icon="circle-alert"),
				shortcut("Schedule Settings", "DocType", "Task Schedule Settings", icon="settings"),
				shortcut("Task Templates", "DocType", "Task Template", doc_view="List", icon="copy-check"),
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
				card("Owner Actions and Follow Ups"),
				link("1. Create Owner Action", "DocType", "Owner Task"),
				link("2. Schedule On Calendar", "DocType", "Owner Task"),
				link("3. Review Action Summary", "Report", "Owner Action Summary"),
				link("4. Review Open Issues", "Report", "Owner Task Issues"),
				card("Groom Daily Schedule"),
				link("1. Describe Daily Tasks", "DocType", "Task Template"),
				link("2. Configure Generation", "DocType", "Task Schedule Settings"),
				link("3. Open Groom Board", "DocType", "Task"),
				link("4. Review Groom Feedback", "Report", "Owner Task Issues"),
				card("Horse Training Plan"),
				link("1. Review Horses", "DocType", "Horse"),
				link("2. Create Training Template", "DocType", "Horse Training Template"),
				link("3. Schedule Training Action", "DocType", "Owner Task"),
				link("4. Review Training Records", "Report", "Horse Training Records"),
				link("5. Review Care Attention", "Report", "Horse Compliance Alerts"),
				card("Purchase Request To Payment"),
				link("1. Review Groom Request", "Report", "Owner Task Issues"),
				link("2. Schedule Buying Action", "DocType", "Owner Task"),
				link("3. Create Or Review Payment", "DocType", "Transaction Input"),
				card("Polo Applications and Matches"),
				link("1. Add Application Action", "DocType", "Owner Task"),
				link("2. Schedule Important Date", "DocType", "Owner Task"),
				link("3. Review Owner Calendar", "DocType", "Owner Task"),
				card("Setup"),
				link("Task Schedule Settings", "DocType"),
				link("Task Templates", "DocType", "Task Template"),
				link("Horse Training Template", "DocType"),
				link("Groom Profiles", "DocType", "Groom Profile"),
				link("Owner Calendar", "DocType", "Owner Task"),
			],
			"content": [
				content("onboarding", "Owner Dashboard Onboarding", col=12),
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
				content("shortcut", "New Owner Action", col=3),
				content("shortcut", "Today Tasks", col=3),
				content("shortcut", "Owner Calendar", col=3),
				content("shortcut", "Owner Gantt", col=3),
				content("shortcut", "Issues", col=3),
				content("shortcut", "Schedule Settings", col=3),
				content("shortcut", "Task Templates", col=3),
				content("shortcut", "Money Dashboard", col=3),
				content("shortcut", "Horse Management", col=3),
				content("shortcut", "Match Dashboard", col=3),
				spacer(),
				content("card", "Owner Actions and Follow Ups", col=4),
				content("card", "Groom Daily Schedule", col=4),
				content("card", "Horse Training Plan", col=4),
				content("card", "Purchase Request To Payment", col=4),
				content("card", "Polo Applications and Matches", col=4),
				content("card", "Setup", col=4),
			],
			"replace_content_when_missing": ["Owner Actions and Follow Ups"],
			"replace_child_tables": ["shortcuts", "links"],
		},
	)

	upsert_workspace(
		"Horse Management Dashboard",
		{
			"title": "Horse Management Dashboard",
			"icon": "heart-handshake",
			"indicator_color": "blue",
			"parent_page": "Poloway",
			"dashboard_onboarding": "Horse Management Onboarding",
			"replace_onboardings": ["Poloway System Onboarding"],
			"roles": ["Horse Owner", "Stable Manager", "System Manager"],
			"shortcuts": [
				shortcut("Horses", "DocType", "Horse", doc_view="List", icon="heart-handshake"),
				shortcut("New Horse", "DocType", "Horse", doc_view="New", icon="plus"),
				shortcut("Care Entry", "DocType", "Horse Care Entry", doc_view="New", icon="clipboard-plus"),
				shortcut("Horse Performance", "Report", "Horse Performance Summary", icon="activity"),
				shortcut("Compliance", "Report", "Horse Compliance Alerts", icon="shield-alert"),
				shortcut("Training Templates", "DocType", "Horse Training Template", doc_view="List", icon="copy-check"),
				shortcut("Medical Records", "Report", "Horse Medical Records", icon="stethoscope"),
				url_shortcut("Money Dashboard", "/app/money-dashboard", icon="circle-dollar-sign"),
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
				card("Bring A Horse Into The Yard"),
				link("1. Create Horse Profile", "DocType", "Horse"),
				link("2. Assign Owner", "DocType", "Horse Owner"),
				link("3. Set Location", "DocType", "Horse Location"),
				link("4. Add Handling And Availability", "DocType", "Horse"),
				link("5. Review Horse Performance", "Report", "Horse Performance Summary"),
				card("Record Daily Horse Care"),
				link("1. Open Care Entry", "DocType", "Horse Care Entry"),
				link("2. Add Feeding Entry", "Report", "Horse Feeding Records"),
				link("3. Add Training Entry", "Report", "Horse Training Records"),
				link("4. Add Medical Note", "Report", "Horse Medical Records"),
				link("5. Review Compliance", "Report", "Horse Compliance Alerts"),
				card("Plan And Record Training"),
				link("1. Create Training Template", "DocType", "Horse Training Template"),
				link("2. Schedule Training Task", "DocType", "Owner Task"),
				link("3. Record Training Session", "DocType", "Horse Training Record"),
				link("4. Review Training History", "Report", "Horse Training Records"),
				link("5. Review Readiness", "Report", "Horse Performance Summary"),
				card("Manage Feeding And Stock"),
				link("1. Review Food Items", "DocType", "Item"),
				link("2. Record Feeding", "DocType", "Horse Feeding Record"),
				link("3. Review Feeding History", "Report", "Horse Feeding Records"),
				link("4. Check Stock Movement", "Report", "Item Stock Ledger"),
				link("5. Review Horse Expenses", "Report", "Horse Expenses"),
				card("Medical And Follow Up"),
				link("1. Create Medical Record", "DocType", "Horse Medical Record"),
				link("2. Set Responsible Person", "DocType", "Horse Medical Record"),
				link("3. Add Next Due Date", "DocType", "Horse Medical Record"),
				link("4. Review Medical History", "Report", "Horse Medical Records"),
				link("5. Review Due Or Overdue Care", "Report", "Horse Compliance Alerts"),
				card("People And Costs"),
				link("1. Review Grooms", "DocType", "Groom Profile"),
				link("2. Review Horse Owners", "DocType", "Horse Owner"),
				link("3. Record Horse Cost", "DocType", "Transaction Input"),
				link("4. Review Horse Expenses", "Report", "Horse Expenses"),
				card("Setup"),
				link("Horse Owners", "DocType", "Horse Owner"),
				link("Horse Locations", "DocType", "Horse Location"),
				link("Training Templates", "DocType", "Horse Training Template"),
				link("Groom Profiles", "DocType", "Groom Profile"),
				link("Food And Care Items", "DocType", "Item"),
			],
			"content": [
				content("onboarding", "Horse Management Onboarding", col=12),
				content("number_card", "Available Horses", col=3),
				content("number_card", "Horses Needing Attention", col=3),
				content("number_card", "Medical Due", col=3),
				content("number_card", "Training Sessions", col=3),
				content("chart", "Horse Readiness", col=12),
				content("custom_block", "Poloway Horse Performance", col=12),
				spacer(),
				content("shortcut", "Horses", col=3),
				content("shortcut", "New Horse", col=3),
				content("shortcut", "Care Entry", col=3),
				content("shortcut", "Horse Performance", col=3),
				content("shortcut", "Compliance", col=3),
				content("shortcut", "Training Templates", col=3),
				content("shortcut", "Medical Records", col=3),
				content("shortcut", "Money Dashboard", col=3),
				spacer(),
				content("card", "Bring A Horse Into The Yard", col=4),
				content("card", "Record Daily Horse Care", col=4),
				content("card", "Plan And Record Training", col=4),
				content("card", "Manage Feeding And Stock", col=4),
				content("card", "Medical And Follow Up", col=4),
				content("card", "People And Costs", col=4),
				content("card", "Setup", col=4),
			],
			"replace_content_when_missing": ["Bring A Horse Into The Yard"],
			"replace_child_tables": ["shortcuts", "links"],
		},
	)

	upsert_workspace(
		"Match Dashboard",
		{
			"title": "Match Dashboard",
			"icon": "trophy",
			"indicator_color": "orange",
			"parent_page": "Poloway",
			"dashboard_onboarding": "Match Dashboard Onboarding",
			"replace_onboardings": ["Poloway System Onboarding"],
			"roles": ["Horse Groom", "Horse Owner", "Stable Manager", "System Manager"],
			"shortcuts": [
				shortcut("Match Days", "DocType", "Match Day", doc_view="List", icon="flag"),
				shortcut("New Match Day", "DocType", "Match Day", doc_view="New", icon="plus"),
				shortcut("Upcoming Polo", "Report", "Upcoming Polo Schedule", icon="calendar-days"),
				shortcut("Polo Performance", "Report", "Polo Performance Summary", icon="trophy"),
				shortcut("Match Board", "Report", "Match Day Board", icon="columns-3"),
				shortcut("Travel", "DocType", "Travel Manifest", doc_view="List", icon="truck"),
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
				card("Apply And Schedule A Match"),
				link("1. Create Application Action", "DocType", "Owner Task"),
				link("2. Create Match Day", "DocType", "Match Day"),
				link("3. Confirm Date On Calendar", "DocType", "Owner Task"),
				link("4. Review Upcoming Polo", "Report", "Upcoming Polo Schedule"),
				card("Prepare Horses And Tack"),
				link("1. Review Horse Readiness", "Report", "Horse Performance Summary"),
				link("2. Choose Match Horses", "DocType", "Match Day"),
				link("3. Configure Tack", "DocType", "Horse Tack Configuration"),
				link("4. Review Match Board", "Report", "Match Day Board"),
				card("Plan Travel And Logistics"),
				link("1. Create Travel Manifest", "DocType", "Travel Manifest"),
				link("2. Add Horses To Travel", "DocType", "Travel Manifest"),
				link("3. Create Owner Follow Ups", "DocType", "Owner Task"),
				link("4. Review Upcoming Polo", "Report", "Upcoming Polo Schedule"),
				card("Run Match Day Work"),
				link("1. Open Match Board", "Report", "Match Day Board"),
				link("2. Open Groom Task Board", "DocType", "Task"),
				link("3. Record Horse Care", "DocType", "Horse Care Entry"),
				link("4. Review Issues", "Report", "Owner Task Issues"),
				card("Review Result And Performance"),
				link("1. Update Match Day", "DocType", "Match Day"),
				link("2. Review Polo Performance", "Report", "Polo Performance Summary"),
				link("3. Review Horse Performance", "Report", "Horse Performance Summary"),
				link("4. Create Follow Up Action", "DocType", "Owner Task"),
				card("Setup"),
				link("Match Days", "DocType", "Match Day"),
				link("Travel Manifests", "DocType", "Travel Manifest"),
				link("Tack Configurations", "DocType", "Horse Tack Configuration"),
				link("Task Templates", "DocType", "Task Template"),
				link("Owner Calendar", "DocType", "Owner Task"),
			],
			"content": [
				content("onboarding", "Match Dashboard Onboarding", col=12),
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
				content("shortcut", "Owner Calendar", col=3),
				content("shortcut", "Today Tasks", col=3),
				spacer(),
				content("card", "Apply And Schedule A Match", col=4),
				content("card", "Prepare Horses And Tack", col=4),
				content("card", "Plan Travel And Logistics", col=4),
				content("card", "Run Match Day Work", col=4),
				content("card", "Review Result And Performance", col=4),
				content("card", "Setup", col=4),
			],
			"replace_content_when_missing": ["Apply And Schedule A Match"],
			"replace_child_tables": ["shortcuts", "links"],
		},
	)

	upsert_workspace(
		"Money Dashboard",
		{
			"title": "Money Dashboard",
			"icon": "circle-dollar-sign",
			"indicator_color": "green",
			"parent_page": "Poloway",
			"dashboard_onboarding": "Money Dashboard Onboarding",
			"replace_onboardings": ["Poloway System Onboarding"],
			"roles": ["Horse Owner", "Stable Manager", "System Manager"],
			"shortcuts": [
				url_shortcut("Upload Receipt", "/app/money-dashboard?upload_receipt=1", icon="receipt-text"),
				shortcut("New Transaction", "DocType", "Transaction Input", doc_view="New", icon="circle-dollar-sign"),
				shortcut("New Purchase", "DocType", "Purchase", doc_view="New", icon="shopping-cart"),
				shortcut("New Item", "DocType", "Item", doc_view="New", icon="package-plus"),
				shortcut("New Quote", "DocType", "Vendor Quote", doc_view="New", icon="scale"),
				shortcut("Ledger", "Report", "Financial Ledger", icon="book-open"),
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
				card("Buy Something"),
				link("1. Open Purchase", "DocType", "Purchase"),
				link("2. Record Payment", "DocType", "Transaction Input"),
				link("3. Check Ledger", "Report", "Financial Ledger"),
				link("4. Review Money Flow", "Report", "Money Flow Summary"),
				card("New Item With Quotes"),
				link("1. Create Item", "DocType", "Item"),
				link("2. Add Vendor", "DocType", "Vendor"),
				link("3. Capture Vendor Quote", "DocType", "Vendor Quote"),
				link("4. Compare Quotes", "Report", "Quote Comparison"),
				link("5. Create Purchase", "DocType", "Purchase"),
				link("6. Pay From Transaction Input", "DocType", "Transaction Input"),
				link("7. Review Item Cost", "Report", "Item Cost History"),
				card("Horse Feed Purchase"),
				link("1. Open Food Items", "DocType", "Item"),
				link("2. Check Feed Stock", "Report", "Item Stock Ledger"),
				link("3. Create Feed Purchase", "DocType", "Purchase"),
				link("4. Record Supplier Payment", "DocType", "Transaction Input"),
				link("5. Review Horse Expenses", "Report", "Horse Expenses"),
				card("Employee Pay"),
				link("1. Open Groom Profile", "DocType", "Groom Profile"),
				link("2. Manage Autopayments", "DocType", "Autopayments"),
				link("3. Record Manual Salary", "DocType", "Transaction Input"),
				link("4. Review Payroll Ledger", "Report", "Financial Ledger"),
				card("Receipts and Review"),
				link("1. Upload or Review Receipt", "DocType", "Receipt Import"),
				link("2. Review Extracted Transaction", "DocType", "Transaction Input"),
				link("3. Review Unposted Transactions", "Report", "Unposted Transactions"),
				link("4. Review Spending", "Report", "Spending By Category"),
				link("5. Review Financial Overview", "Report", "Financial Overview"),
				card("Setup"),
				link("Money Accounts", "DocType", "Money Account"),
				link("Vendors", "DocType", "Vendor"),
				link("Item Categories", "DocType", "Item Category"),
				link("Inventory Locations", "DocType", "Inventory Location"),
				link("Autopayment Rules", "DocType", "Autopayments"),
			],
			"content": [
				content("onboarding", "Money Dashboard Onboarding", col=12),
				content("number_card", "Income", col=2),
				content("number_card", "Outflow", col=2),
				content("number_card", "Net Cash Flow", col=2),
				content("number_card", "Stock Value", col=3),
				content("number_card", "Open Quotes", col=3),
				content("chart", "Money Flow", col=6),
				content("chart", "Spending Breakdown", col=6),
				content("chart", "Inventory Value", col=12),
				spacer(),
				content("shortcut", "Upload Receipt", col=3),
				content("shortcut", "New Transaction", col=3),
				content("shortcut", "New Purchase", col=3),
				content("shortcut", "New Item", col=3),
				content("shortcut", "New Quote", col=3),
				content("shortcut", "Ledger", col=3),
				content("shortcut", "Autopayments", col=3),
				spacer(),
				content("card", "Buy Something", col=4),
				content("card", "New Item With Quotes", col=4),
				content("card", "Horse Feed Purchase", col=4),
				content("card", "Employee Pay", col=4),
				content("card", "Receipts and Review", col=4),
				content("card", "Setup", col=4),
			],
			"replace_content_when_missing": ["Buy Something"],
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
		sidebar_section("Dashboards"),
		sidebar_link("Poloway Home", "Workspace", "Poloway", icon="home"),
		sidebar_link("Owner Dashboard", "Workspace", "Owner Dashboard", icon="layout-dashboard"),
		sidebar_link("Money Dashboard", "Workspace", "Money Dashboard", icon="circle-dollar-sign"),
		sidebar_link("Horse Management Dashboard", "Workspace", "Horse Management Dashboard", icon="heart-handshake"),
		sidebar_link("Match Dashboard", "Workspace", "Match Dashboard", icon="trophy"),
		sidebar_link("Groom Dashboard", "Workspace", "Groom Dashboard", icon="list-todo"),

		sidebar_section("Owner & Scheduling"),
		sidebar_link("Owner Tasks", "DocType", "Owner Task", icon="calendar-days", child=1),
		sidebar_link("Owner Calendar", "DocType", "Owner Task", icon="calendar-days", child=1),
		sidebar_link("Task Schedule Settings", "DocType", "Task Schedule Settings", icon="settings", child=1),
		sidebar_link("Task Templates", "DocType", "Task Template", icon="copy-check", child=1),
		sidebar_link("Task List", "DocType", "Task", icon="list", child=1),
		sidebar_link("Owner Action Summary", "Report", "Owner Action Summary", child=1),
		sidebar_link("Owner Task Issues", "Report", "Owner Task Issues", icon="circle-alert", child=1),

		sidebar_section("Groom Work"),
		sidebar_url("Today Tasks", "/app/task/view/kanban/Whiteboard", icon="kanban", child=1),
		sidebar_link("Groom Profiles", "DocType", "Groom Profile", icon="users", child=1),
		sidebar_link("Horse Care Entry", "DocType", "Horse Care Entry", icon="clipboard-plus", child=1),

		sidebar_section("Horse Management"),
		sidebar_link("Horses", "DocType", "Horse", icon="heart-handshake", child=1),
		sidebar_link("Horse Owners", "DocType", "Horse Owner", child=1),
		sidebar_link("Horse Locations", "DocType", "Horse Location", child=1),
		sidebar_link("Horse Feeding Records", "DocType", "Horse Feeding Record", child=1),
		sidebar_link("Horse Training Records", "DocType", "Horse Training Record", child=1),
		sidebar_link("Horse Medical Records", "DocType", "Horse Medical Record", child=1),
		sidebar_link("Horse Training Templates", "DocType", "Horse Training Template", child=1),
		sidebar_link("Horse Feeding Report", "Report", "Horse Feeding Records", child=1),
		sidebar_link("Horse Training Report", "Report", "Horse Training Records", child=1),
		sidebar_link("Horse Medical Report", "Report", "Horse Medical Records", child=1),
		sidebar_link("Horse Performance Summary", "Report", "Horse Performance Summary", child=1),
		sidebar_link("Horse Compliance Alerts", "Report", "Horse Compliance Alerts", child=1),
		sidebar_link("Horse Expenses", "Report", "Horse Expenses", child=1),

		sidebar_section("Matches & Travel"),
		sidebar_link("Match Days", "DocType", "Match Day", icon="flag", child=1),
		sidebar_link("Travel Manifest", "DocType", "Travel Manifest", child=1),
		sidebar_link("Horse Tack Configuration", "DocType", "Horse Tack Configuration", child=1),
		sidebar_link("Upcoming Polo Schedule", "Report", "Upcoming Polo Schedule", child=1),
		sidebar_link("Polo Performance Summary", "Report", "Polo Performance Summary", child=1),
		sidebar_link("Match Day Board", "Report", "Match Day Board", child=1),

		sidebar_section("Money & Inventory"),
		sidebar_link("Transaction Input", "DocType", "Transaction Input", child=1),
		sidebar_link("Payment Ledger Entries", "DocType", "Payment Ledger Entry", child=1),
		sidebar_link("Receipt Import", "DocType", "Receipt Import", child=1),
		sidebar_link("Purchase", "DocType", "Purchase", child=1),
		sidebar_link("Vendor Quote", "DocType", "Vendor Quote", child=1),
		sidebar_link("Vendor", "DocType", "Vendor", child=1),
		sidebar_link("Item", "DocType", "Item", child=1),
		sidebar_link("Item Category", "DocType", "Item Category", child=1),
		sidebar_link("Item Stock Ledger Entries", "DocType", "Item Stock Ledger", child=1),
		sidebar_link("Inventory Location", "DocType", "Inventory Location", child=1),
		sidebar_link("Stock Adjustment", "DocType", "Stock Adjustment", child=1),
		sidebar_link("Autopayments", "DocType", "Autopayments", child=1),
		sidebar_link("Money Account", "DocType", "Money Account", child=1),
		sidebar_link("Financial Overview", "Report", "Financial Overview", child=1),
		sidebar_link("Money Flow Summary", "Report", "Money Flow Summary", child=1),
		sidebar_link("Spending By Category", "Report", "Spending By Category", child=1),
		sidebar_link("Financial Ledger", "Report", "Financial Ledger", child=1),
		sidebar_link("Quote Comparison", "Report", "Quote Comparison", child=1),
		sidebar_link("Unposted Transactions", "Report", "Unposted Transactions", child=1),
		sidebar_link("Inventory Vendor Summary", "Report", "Inventory Vendor Summary", child=1),
		sidebar_link("Item Cost History", "Report", "Item Cost History", child=1),
		sidebar_link("Item Stock Ledger Report", "Report", "Item Stock Ledger", child=1),
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
		icon.icon_type = "Link"
		icon.link_type = "Workspace Sidebar"
		icon.link_to = "Poloway"
		icon.sidebar = "Poloway"
		icon.hidden = 0
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

	ensure_workspace_onboarding_content(
		workspace,
		config.get("dashboard_onboarding"),
		config.get("replace_onboardings"),
	)

	if not workspace_exists and name == "Poloway":
		remove_child_rows(
			workspace,
			"custom_blocks",
			lambda row: row.get("custom_block_name") == "Poloway Onboarding",
		)

	seed_child_rows_if_empty(workspace, "shortcuts", config["shortcuts"])
	seed_child_rows_if_empty(workspace, "links", config["links"])
	seed_child_rows_if_empty(workspace, "number_cards", config.get("number_cards", []))
	seed_child_rows_if_empty(workspace, "charts", config.get("charts", []))
	seed_child_rows_if_empty(workspace, "custom_blocks", config.get("custom_blocks", []))
	merge_child_rows(workspace, "roles", [{"role": role} for role in config["roles"]], role_key)

	workspace.save(ignore_permissions=True)


def ensure_workspace_onboarding_content(workspace, onboarding_name, replace_onboardings=None):
	if not onboarding_name:
		return

	try:
		content_rows = frappe.parse_json(workspace.content) or []
	except Exception:
		content_rows = []

	replace_onboardings = set(replace_onboardings or [])
	target_row = None
	changed = False
	filtered_rows = []
	for row in content_rows:
		if row.get("type") != "onboarding":
			filtered_rows.append(row)
			continue

		current_name = (row.get("data") or {}).get("onboarding_name")
		if current_name == onboarding_name:
			if target_row is None:
				target_row = row
			changed = True
		elif current_name in replace_onboardings:
			changed = True
		else:
			filtered_rows.append(row)

	if target_row is None:
		target_row = content("onboarding", onboarding_name, col=12)
		changed = True

	filtered_rows.insert(0, target_row)

	if changed:
		workspace.content = frappe.as_json(filtered_rows)


def seed_child_rows_if_empty(doc, table_field, rows):
	if doc.get(table_field):
		return
	for row in rows:
		doc.append(table_field, row)


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
		"Poloway Home: System Overview",
		["Horse Owner", "Stable Manager", "System Manager"],
		[
			upsert_onboarding_step(
				"Open the Poloway home dashboard",
				"Go to Page",
				"Start with the main owner view. This dashboard is the big-picture cockpit: financial snapshot, upcoming polo, horse performance, owner actions, receipt upload, and links into each operating area.",
				action_label="Open Home Dashboard",
				path="/app/poloway",
				callback_title="Poloway Home",
				callback_message="Use this as the first screen after login. It is for quick direction, not detailed entry.",
			),
			upsert_onboarding_step(
				"Understand the Poloway operating map",
				"Go to Page",
				"Poloway is split into four operating areas: Owner and Scheduling, Horse Management, Money and Inventory, and Match Operations. The home dashboard shows the health of all four, then sends you into the right area for real work.",
				action_label="Review Home",
				path="/app/poloway",
				callback_title="How to think about Poloway",
				callback_message="Start at Home for the picture, use a specialist dashboard for action, and use reports when you need proof or history.",
			),
			upsert_onboarding_step(
				"Open the owner actions dashboard",
				"Go to Page",
				"The owner dashboard is for decisions and instructions: owner tasks, calendar planning, groom schedules, follow-ups, and issue review.",
				action_label="Open Owner Dashboard",
				path="/app/owner-dashboard",
				callback_title="Owner Dashboard",
				callback_message="Use this area when the owner needs to create an action, schedule something, or review what needs attention.",
			),
			upsert_onboarding_step(
				"Open the horse management dashboard",
				"Go to Page",
				"The horse management dashboard is for profiles, care history, feeding, training, medical records, compliance, and horse-level costs.",
				action_label="Open Horse Management",
				path="/app/horse-management-dashboard",
				callback_title="Horse Management Dashboard",
				callback_message="Use this dashboard when the question is about a horse, its care, its condition, or its performance.",
			),
			upsert_onboarding_step(
				"Open the groom dashboard",
				"Go to Page",
				"The groom dashboard and task board show the daily work list. Owners use the setup steps to decide what appears for the groom.",
				action_label="Open Groom Dashboard",
				path="/app/groom-dashboard",
				callback_title="Groom Dashboard",
				callback_message="This is the groom-facing operating surface: today, open work, completion notes, and issues.",
			),
			upsert_onboarding_step(
				"Open the money dashboard",
				"Go to Page",
				"The money dashboard is for purchases, quotes, vendors, items, receipts, unposted transactions, and the immutable ledger.",
				action_label="Open Money Dashboard",
				path="/app/money-dashboard",
				callback_title="Money Dashboard",
				callback_message="Use this area when money, stock, vendors, purchases, receipts, or payroll are involved.",
			),
			upsert_onboarding_step(
				"Open the match dashboard",
				"Go to Page",
				"The match dashboard is for polo applications, match days, horse readiness, tack, travel, chukkers, and post-game performance.",
				action_label="Open Match Dashboard",
				path="/app/match-dashboard",
				callback_title="Match Dashboard",
				callback_message="Use this area when the question is about an upcoming game or tournament day.",
			),
			upsert_onboarding_step(
				"Create the first horse profile",
				"Create Entry",
				"Create a complete horse profile. This starts the Horse Profile Basics form tour and walks through stable name, registration, location, handling, playing, availability, ownership, and linked records.",
				reference_document="Horse",
				action_label="Create Horse",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Horse Profile Basics",
			),
			upsert_onboarding_step(
				"Create a groom profile",
				"Create Entry",
				"Create the groom profile so tasks, payroll, and owner reporting can link work to the right person.",
				reference_document="Groom Profile",
				action_label="Create Groom Profile",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Groom Profile Basics",
			),
			upsert_onboarding_step(
				"Create an owner action",
				"Create Entry",
				"Create an owner task for something the owner must do or decide: apply for a polo game, buy something, schedule training, call a supplier, or follow up on a groom issue.",
				reference_document="Owner Task",
				action_label="Create Owner Action",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Owner Action Basics",
			),
			upsert_onboarding_step(
				"Create inventory items",
				"Create Entry",
				"Create feed, tack, medicine, supplies, services, horses, and other items before using them in feeding, receipts, stock, quotes, and financial entries.",
				reference_document="Item",
				action_label="Create Item",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Item Basics",
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
				"Review money flow",
				"View Report",
				"Open the money flow report to understand income, outflow, and net cash flow.",
				reference_report="Money Flow Summary",
				action_label="View Money Flow",
				report_description="This report powers the owner money dashboard and shows the big financial picture.",
			),
			upsert_onboarding_step(
				"Review upcoming polo",
				"View Report",
				"Open the upcoming polo schedule to see the next events and dates that matter.",
				reference_report="Upcoming Polo Schedule",
				action_label="View Upcoming Polo",
				report_description="This report feeds the home dashboard and match dashboard.",
			),
		],
	)

	upsert_module_onboarding(
		"Owner Dashboard Onboarding",
		"Owner Dashboard: Decisions, Scheduling, and Follow-Up",
		["Horse Owner", "Stable Manager", "System Manager"],
		[
			upsert_onboarding_step(
				"Open the owner actions dashboard",
				"Go to Page",
				"The owner dashboard is for decisions and instructions: owner tasks, calendar planning, groom schedules, follow-ups, and issue review.",
				action_label="Open Owner Dashboard",
				path="/app/owner-dashboard",
				callback_title="Owner Dashboard",
				callback_message="Use this area when the owner needs to create an action, schedule something, or review what needs attention.",
			),
			upsert_onboarding_step(
				"Create an owner action",
				"Create Entry",
				"Create an owner task for something the owner must do or decide: apply for a polo game, buy something, schedule training, call a supplier, or follow up on a groom issue.",
				reference_document="Owner Task",
				action_label="Create Owner Action",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Owner Action Basics",
			),
			upsert_onboarding_step(
				"Review the owner calendar",
				"Go to Page",
				"Open the owner calendar to see upcoming applications, purchases, tournaments, calls, and owner follow-ups in date order.",
				action_label="Open Owner Calendar",
				path="/app/owner-task/view/calendar",
				callback_title="Owner Calendar",
				callback_message="Calendar and Gantt are the best owner-facing views for time-based responsibilities.",
			),
			upsert_onboarding_step(
				"Review the owner gantt",
				"Go to Page",
				"Use the Gantt view when owner actions stretch across several days, such as travel preparation, buying tack, or tournament planning.",
				action_label="Open Owner Gantt",
				path="/app/owner-task/view/gantt",
				callback_title="Owner Gantt",
				callback_message="Use calendar for dates, Gantt for timeline planning, and reports for issue review.",
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
				show_form_tour=1,
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
				"Review owner issues",
				"View Report",
				"Open the owner issue report to see groom-reported problems, unresolved notes, and items needing acknowledgement.",
				reference_report="Owner Task Issues",
				action_label="View Owner Issues",
				report_description="This is the owner follow-up queue for things that went wrong or need attention.",
			),
			upsert_onboarding_step(
				"Review owner action summary",
				"View Report",
				"Use the owner action summary to see open, completed, and overdue owner-side work.",
				reference_report="Owner Action Summary",
				action_label="View Owner Actions",
				report_description="This report summarizes the work the owner or manager still needs to do.",
			),
			upsert_onboarding_step(
				"Open the money dashboard",
				"Go to Page",
				"The owner dashboard links into money when a groom request or owner action turns into a purchase or payment.",
				action_label="Open Money Dashboard",
				path="/app/money-dashboard",
				callback_title="Money Dashboard",
				callback_message="Purchase requests should become Purchase or Transaction Input records from the money area.",
			),
			upsert_onboarding_step(
				"Open the match dashboard",
				"Go to Page",
				"The owner dashboard links into matches when an action becomes a tournament application, match day, or travel plan.",
				action_label="Open Match Dashboard",
				path="/app/match-dashboard",
				callback_title="Match Dashboard",
				callback_message="Use match operations once a polo action has a real event date or game context.",
			),
		],
	)

	upsert_module_onboarding(
		"Horse Management Onboarding",
		"Horse Management: Profiles, Care, and Performance",
		["Horse Owner", "Stable Manager", "System Manager"],
		[
			upsert_onboarding_step(
				"Open the horse management dashboard",
				"Go to Page",
				"The horse management dashboard is for profiles, care history, feeding, training, medical records, compliance, and horse-level costs.",
				action_label="Open Horse Management",
				path="/app/horse-management-dashboard",
				callback_title="Horse Management Dashboard",
				callback_message="Use this dashboard when the question is about a horse, its care, its condition, or its performance.",
			),
			upsert_onboarding_step(
				"Create the first horse profile",
				"Create Entry",
				"Create a complete horse profile. This starts the Horse Profile Basics form tour and walks through stable name, registration, location, handling, playing, availability, ownership, and linked records.",
				reference_document="Horse",
				action_label="Create Horse",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Horse Profile Basics",
			),
			upsert_onboarding_step(
				"Create a horse training template",
				"Create Entry",
				"Create repeatable training templates so daily work can be planned consistently and training records stay comparable.",
				reference_document="Horse Training Template",
				action_label="Create Training Template",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Horse Training Template Basics",
			),
			upsert_onboarding_step(
				"Create a horse care entry",
				"Create Entry",
				"Use Horse Care Entry when one real-world action should create feeding, training, or medical records from a single place.",
				reference_document="Horse Care Entry",
				action_label="Create Care Entry",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Horse Care Entry Basics",
			),
			upsert_onboarding_step(
				"Tour feeding records",
				"Show Form Tour",
				"Learn how feeding records link one horse, one food item, quantity, timing, responsible person, and notes.",
				reference_document="Horse Feeding Record",
				action_label="Start Feeding Tour",
				show_form_tour=1,
				form_tour="Horse Feeding Record Basics",
			),
			upsert_onboarding_step(
				"Tour training records",
				"Show Form Tour",
				"Learn how training records capture templates, work type, duration, intensity, outcome, ratings, and notes.",
				reference_document="Horse Training Record",
				action_label="Start Training Tour",
				show_form_tour=1,
				form_tour="Horse Training Record Basics",
			),
			upsert_onboarding_step(
				"Tour medical records",
				"Show Form Tour",
				"Learn how medical records capture all medical events and link them to the responsible person, not only a veterinarian.",
				reference_document="Horse Medical Record",
				action_label="Start Medical Tour",
				show_form_tour=1,
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
				"Review horse expenses",
				"View Report",
				"Open the horse expenses report when you need to understand what each horse is costing.",
				reference_report="Horse Expenses",
				action_label="View Horse Expenses",
				report_description="This links the horse model back to money without using the horse profile as the transaction entry point.",
			),
		],
	)

	upsert_module_onboarding(
		"Groom Dashboard Onboarding",
		"Groom Dashboard: Daily Work and Feedback",
		["Horse Groom", "Stable Manager", "System Manager"],
		[
			upsert_onboarding_step(
				"Open the groom dashboard",
				"Go to Page",
				"The groom dashboard and task board show the daily work list. Owners use the setup steps to decide what appears for the groom.",
				action_label="Open Groom Dashboard",
				path="/app/groom-dashboard",
				callback_title="Groom Dashboard",
				callback_message="This is the groom-facing operating surface: today, open work, completion notes, and issues.",
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
				"Tour a groom task",
				"Show Form Tour",
				"Learn what the groom sees on a task: instructions, horse, due time, auto-created care records, completion notes, and issue fields.",
				reference_document="Task",
				action_label="Start Task Tour",
				show_form_tour=1,
				form_tour="Groom Task Basics",
			),
			upsert_onboarding_step(
				"Create a horse care entry",
				"Create Entry",
				"Use Horse Care Entry when one real-world action should create feeding, training, or medical records from a single place.",
				reference_document="Horse Care Entry",
				action_label="Create Care Entry",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Horse Care Entry Basics",
			),
			upsert_onboarding_step(
				"Tour feeding records",
				"Show Form Tour",
				"Learn how feeding records link one horse, one food item, quantity, timing, responsible person, and notes.",
				reference_document="Horse Feeding Record",
				action_label="Start Feeding Tour",
				show_form_tour=1,
				form_tour="Horse Feeding Record Basics",
			),
			upsert_onboarding_step(
				"Tour training records",
				"Show Form Tour",
				"Learn how training records capture templates, work type, duration, intensity, outcome, ratings, and notes.",
				reference_document="Horse Training Record",
				action_label="Start Training Tour",
				show_form_tour=1,
				form_tour="Horse Training Record Basics",
			),
			upsert_onboarding_step(
				"Tour medical records",
				"Show Form Tour",
				"Learn how medical records capture all medical events and link them to the responsible person, not only a veterinarian.",
				reference_document="Horse Medical Record",
				action_label="Start Medical Tour",
				show_form_tour=1,
				form_tour="Horse Medical Record Basics",
			),
			upsert_onboarding_step(
				"Open the match day board",
				"View Report",
				"Use the match day board when a groom needs to see game-day horses, tack, travel, and task context.",
				reference_report="Match Day Board",
				action_label="View Match Board",
				report_description="This is the practical match-day preparation view.",
			),
		],
	)

	upsert_module_onboarding(
		"Money Dashboard Onboarding",
		"Money Dashboard: Inventory, Purchases, Receipts, and Ledger",
		["Horse Owner", "Stable Manager", "System Manager"],
		[
			upsert_onboarding_step(
				"Open the money dashboard",
				"Go to Page",
				"The money dashboard is for purchases, quotes, vendors, items, receipts, unposted transactions, and the immutable ledger.",
				action_label="Open Money Dashboard",
				path="/app/money-dashboard",
				callback_title="Money Dashboard",
				callback_message="Use this area when money, stock, vendors, purchases, receipts, or payroll are involved.",
			),
			upsert_onboarding_step(
				"Create a money account",
				"Create Entry",
				"Create or review the chart-style accounts that classify cash, income, expenses, assets, and liabilities.",
				reference_document="Money Account",
				action_label="Create Money Account",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Money Account Basics",
			),
			upsert_onboarding_step(
				"Create an item category",
				"Create Entry",
				"Create the item category tree first so food, tack, medicine, equipment, services, and stock items can inherit sensible defaults.",
				reference_document="Item Category",
				action_label="Create Item Category",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Item Category Basics",
			),
			upsert_onboarding_step(
				"Create an inventory location",
				"Create Entry",
				"Create stock locations such as feed room, tack room, medicine cabinet, vehicle, or yard storage.",
				reference_document="Inventory Location",
				action_label="Create Inventory Location",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Inventory Location Basics",
			),
			upsert_onboarding_step(
				"Create inventory items",
				"Create Entry",
				"Create feed, tack, medicine, supplies, services, horses, and other items before using them in feeding, receipts, stock, quotes, and financial entries.",
				reference_document="Item",
				action_label="Create Item",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Item Basics",
			),
			upsert_onboarding_step(
				"Create vendors",
				"Create Entry",
				"Create suppliers, vets, farriers, transport providers, horse sellers, buyers, and service providers for purchases, quotes, and receipts.",
				reference_document="Vendor",
				action_label="Create Vendor",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Vendor Basics",
			),
			upsert_onboarding_step(
				"Create a purchase",
				"Create Entry",
				"Use Purchase to describe what you intend to buy before quotes and payment: item, horse, service, tournament, feed, tack, or equipment.",
				reference_document="Purchase",
				action_label="Create Purchase",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Purchase Basics",
			),
			upsert_onboarding_step(
				"Capture a vendor quote",
				"Create Entry",
				"Capture one supplier quote for a purchase. Add as many quotes as needed, compare them, then select one before payment.",
				reference_document="Vendor Quote",
				action_label="Create Vendor Quote",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Vendor Quote Basics",
			),
			upsert_onboarding_step(
				"Compare vendor quotes",
				"View Report",
				"Use quote comparison when multiple vendors can satisfy the same purchase and you need to choose the best quote.",
				reference_report="Quote Comparison",
				action_label="Compare Quotes",
				report_description="This report supports the purchase decision before money is recorded.",
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
				"Review unposted transactions",
				"View Report",
				"Open unposted transactions to find drafts created from receipts or manual entry that still need review.",
				reference_report="Unposted Transactions",
				action_label="Review Unposted",
				report_description="This is the queue to clean up before ledger posting.",
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
				"Review the ledger",
				"View Report",
				"Open the financial ledger after transactions and receipt imports have posted.",
				reference_report="Financial Ledger",
				action_label="View Ledger",
				report_description="This is the immutable ledger view for posted financial movement.",
			),
			upsert_onboarding_step(
				"Configure autopayments",
				"Show Form Tour",
				"Use Autopayments for recurring payments such as groom salary. The actual ledger still comes from Transaction Input.",
				reference_document="Autopayments",
				action_label="Configure Autopayments",
				show_form_tour=1,
				form_tour="Autopayments Basics",
			),
		],
	)

	upsert_module_onboarding(
		"Match Dashboard Onboarding",
		"Match Dashboard: Polo Games, Travel, Tack, and Results",
		["Horse Groom", "Horse Owner", "Stable Manager", "System Manager"],
		[
			upsert_onboarding_step(
				"Open the match dashboard",
				"Go to Page",
				"The match dashboard is for polo applications, match days, horse readiness, tack, travel, chukkers, and post-game performance.",
				action_label="Open Match Dashboard",
				path="/app/match-dashboard",
				callback_title="Match Dashboard",
				callback_message="Use this area when the question is about an upcoming game or tournament day.",
			),
			upsert_onboarding_step(
				"Create a match day",
				"Create Entry",
				"Create a match day once an event is being applied for, scheduled, or confirmed. This becomes the hub for teams, chukkers, horses, groom work, and result tracking.",
				reference_document="Match Day",
				action_label="Create Match Day",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Match Day Basics",
			),
			upsert_onboarding_step(
				"Create a travel manifest",
				"Create Entry",
				"Create a travel manifest for away games so horses, kit, driver, vehicle, and destination are managed together.",
				reference_document="Travel Manifest",
				action_label="Create Travel Manifest",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Travel Manifest Basics",
			),
			upsert_onboarding_step(
				"Create a tack configuration",
				"Create Entry",
				"Create tack configurations so match-day prep is repeatable for each horse.",
				reference_document="Horse Tack Configuration",
				action_label="Create Tack Configuration",
				show_full_form=1,
				show_form_tour=1,
				form_tour="Horse Tack Configuration Basics",
			),
			upsert_onboarding_step(
				"Review the match day board",
				"View Report",
				"Open the match day board to review horses, chukkers, tack, travel readiness, and open tasks for a game day.",
				reference_report="Match Day Board",
				action_label="View Match Board",
				report_description="This is the operational board for match preparation and match-day execution.",
			),
			upsert_onboarding_step(
				"Review upcoming polo",
				"View Report",
				"Open the upcoming polo schedule to see the next events and dates that matter.",
				reference_report="Upcoming Polo Schedule",
				action_label="View Upcoming Polo",
				report_description="This report feeds the home dashboard and match dashboard.",
			),
			upsert_onboarding_step(
				"Review polo performance",
				"View Report",
				"Use polo performance after matches to see results, horses used, and trends across games.",
				reference_report="Polo Performance Summary",
				action_label="View Polo Performance",
				report_description="This turns match records into owner-friendly performance context.",
			),
			upsert_onboarding_step(
				"Review horse performance",
				"View Report",
				"Open the horse performance report before a match so horse selection is based on care, readiness, and recent work.",
				reference_report="Horse Performance Summary",
				action_label="View Horse Performance",
				report_description="Use this before assigning horses to chukkers.",
			),
			upsert_onboarding_step(
				"Open the groom task board",
				"Go to Page",
				"Open the groom task board when match preparation becomes real work for the groom.",
				action_label="Open Task Board",
				path="/app/task/view/kanban/Whiteboard",
				callback_title="Groom task board",
				callback_message="Match-day tasks should still be completed through the same groom task workflow.",
			),
		],
	)


def setup_poloway_form_tours():
	for title, doctype, steps in [
		(
			"Owner Action Basics",
			"Owner Task",
			[
				("subject", "Action title", "Write the practical action the owner needs to take or decide."),
				("status", "Status", "Use status to move the action from open to completed or cancelled."),
				("priority", "Priority", "Set priority when an action affects care, tournament timing, money, or a groom issue."),
				("task_type", "Action type", "Separate purchases, tournaments, horse care, calls, scheduling, and general follow-ups."),
				("horse_owner", "Owner context", "Link the owner profile when the action belongs to a specific owner."),
				("horse", "Horse context", "Link the horse when the action is about one horse."),
				("tournament", "Tournament context", "Use this when the action belongs to a polo game or tournament."),
				("due_date", "Due date", "Put the action on the owner calendar by setting the due date."),
				("starts_on", "Calendar timing", "Use start and end times when the action needs a specific slot."),
				("description", "Instructions", "Capture the actual instruction, decision, or context here."),
				("completion_notes", "Completion notes", "Record the outcome so the owner can see what happened later."),
			],
		),
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
			"Horse Care Entry Basics",
			"Horse Care Entry",
			[
				("entry_type", "Entry type", "Choose whether this entry is feeding, training, medical, or a general care note."),
				("horse", "Horse", "Every care entry belongs to the horse it was performed for."),
				("task", "Task link", "Link the groom task when the entry came from a daily task."),
				("entry_date", "Date and time", "Record when the care happened so daily records stay accurate."),
				("feed_item", "Feeding details", "For feeding entries, choose the food item and quantity."),
				("training_template", "Training details", "For training entries, use a template and record work type, duration, and intensity."),
				("medical_record_type", "Medical details", "For medical entries, record the medical type, responsible person, and summary."),
				("notes", "Notes", "Use notes for anything that went differently, needs follow-up, or should be visible to the owner."),
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
			"Horse Training Template Basics",
			"Horse Training Template",
			[
				("template_name", "Template name", "Create a reusable routine such as Fitness Set, Stick and Ball, Recovery Ride, or Match Prep."),
				("default_trainer", "Default trainer", "Set the usual trainer when this routine normally belongs to one person."),
				("description", "Purpose", "Explain when this template should be used and what outcome it is meant to create."),
				("training_items", "Training items", "Break the routine into practical pieces with work type, duration, intensity, and instructions."),
				("is_active", "Active", "Only active templates should be used for new scheduling and training records."),
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
			"Groom Profile Basics",
			"Groom Profile",
			[
				("first_name", "Name", "Create one groom profile per real groom."),
				("user", "Login user", "Link the Frappe user so tasks and permissions connect to this groom."),
				("is_active", "Active", "Only active grooms should receive new task assignments."),
				("phone", "Contact details", "Keep practical contact information available to management."),
				("start_date", "Employment start", "Record when the groom started for management and payroll context."),
				("salary", "Salary", "Salary is used when creating salary transaction inputs and autopayment rules."),
				("overtime_rate", "Overtime", "Capture overtime rate if extra work needs to be recorded separately."),
				("notes", "Notes", "Use notes for employment context, responsibilities, or practical yard information."),
			],
		),
		(
			"Groom Task Basics",
			"Task",
			[
				("subject", "Task title", "The kanban card shows the title, so keep it short and direct."),
				("status", "Status", "Open tasks appear on the groom board; completed tasks leave the day view."),
				("task_type", "Task type", "Task type controls what kind of record can be created from the task."),
				("assigned_to", "Assigned groom", "Assign the user who should see and complete the task."),
				("horse", "Horse", "Link the horse when the work is horse-specific."),
				("due_date", "Due date", "The groom board is filtered to the current day, so due date matters."),
				("starts_on", "Timing", "Use start and end times to order the groom's day."),
				("feed_item", "Feeding automation", "For feeding tasks, set the feed item, quantity, unit, and time."),
				("training_template", "Training automation", "For training tasks, set the training template and work details."),
				("medical_record_type", "Medical automation", "For medical tasks, set the medical type, responsible person, and summary."),
				("instructions", "Instructions", "This is the main detail the groom needs when opening the task."),
				("completion_notes", "Completion notes", "The groom fills this in when completing or reporting an issue."),
				("issue_reported", "Issue reporting", "Use issue fields when something went wrong or needs owner attention."),
			],
		),
		(
			"Money Account Basics",
			"Money Account",
			[
				("account_name", "Account name", "Create clear accounts such as Cash, Bank, Feed Expense, Groom Salaries, Horse Sales, or Tournament Income."),
				("account_type", "Account type", "Use account type to classify asset, liability, equity, income, and expense accounts."),
				("root_type", "Debit or credit", "Root type controls the accounting side of the account in the double-entry ledger."),
				("is_cash_account", "Cash or bank", "Enable this for accounts that represent actual cash, bank, card, or wallet balances."),
				("is_active", "Active", "Deactivate accounts you no longer want used for new transactions."),
				("description", "Description", "Use this to explain when the account should be selected."),
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
			"Item Category Basics",
			"Item Category",
			[
				("item_category_name", "Category name", "Build clear category names such as Food, Tack, Medicine, Horse Equipment, Saddles, or Bits."),
				("parent_item_category", "Parent category", "Use the tree to group broad categories and expand into subcategories later."),
				("is_group", "Group category", "Enable this for categories that hold child categories instead of direct items."),
				("category_type", "Category type", "Category type drives filtering, especially food-only selections for feeding records."),
				("description", "Description", "Explain what belongs in the category so future setup stays consistent."),
				("default_inventory_location", "Default location", "Set where items in this category normally live."),
				("default_unit", "Default unit", "Use default unit for feed, medicine, tack, and supplies."),
				("default_responsible_role", "Default responsibility", "Use defaults to assign responsibility by category."),
			],
		),
		(
			"Inventory Location Basics",
			"Inventory Location",
			[
				("location_name", "Location name", "Create practical locations such as Feed Room, Tack Room, Medicine Cabinet, Vehicle, or Stable Yard."),
				("parent_inventory_location", "Parent location", "Use the tree to nest storage areas under a broader yard or facility."),
				("is_group", "Group location", "Enable this when the location only groups child locations."),
				("location_type", "Location type", "Choose the type so stock reports can separate rooms, yards, vehicles, and storage."),
				("responsible_user", "Responsible user", "Assign the person responsible for stock in this location."),
				("notes", "Notes", "Use notes for shelf, security, access, or handling instructions."),
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
			"Purchase Basics",
			"Purchase",
			[
				("purchase_title", "Purchase title", "Describe what is being bought, such as feed restock, saddle, vet treatment, transport, or horse purchase."),
				("status", "Status", "Track the purchase from draft to quoted, selected, ordered, paid, received, or cancelled."),
				("purchase_date", "Purchase date", "Use the date the request was created or purchase process started."),
				("needed_by", "Needed by", "Set the deadline when the item or service must be ready."),
				("purchase_category", "Category", "Use category to separate feed, tack, equipment, horse purchases, tournament costs, and services."),
				("linked_horse", "Horse context", "Link a horse when the purchase belongs to one horse."),
				("tournament", "Tournament context", "Use tournament or event context when the purchase belongs to polo operations."),
				("selected_quote", "Selected quote", "After comparing quotes, store the chosen quote here."),
				("transaction_input", "Transaction input", "When paid, the purchase should flow into Transaction Input and then ledger entries."),
				("lines", "Purchase lines", "Add the items, horses, or services being bought."),
				("estimated_total", "Estimated total", "This is the expected total before final payment or receipt matching."),
				("notes", "Notes", "Keep owner decisions, supplier context, or purchase reasoning here."),
			],
		),
		(
			"Vendor Quote Basics",
			"Vendor Quote",
			[
				("quote_title", "Quote title", "Give each quote a clear name so comparisons are readable."),
				("vendor", "Vendor", "Choose the supplier, seller, vet, farrier, or provider giving this quote."),
				("status", "Status", "Use status to separate draft, submitted, selected, rejected, and expired quotes."),
				("quote_date", "Quote date", "Record when the quote was received."),
				("valid_until", "Valid until", "Set expiry dates so old quotes do not drive decisions."),
				("purchase", "Purchase", "Link the quote to the purchase it is competing for."),
				("linked_horse", "Horse context", "Link a horse when the quote belongs to one horse."),
				("quote_file", "Quote file", "Attach the quote or receipt file when available."),
				("lines", "Quote lines", "Capture quoted items, horses, services, quantity, rate, and tax."),
				("total_amount", "Total amount", "The total is used in quote comparison and selection."),
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
			"Autopayments Basics",
			"Autopayments",
			[
				("enabled", "Enable autopayments", "Turn this on only when recurring payments should be generated automatically."),
				("rules", "Rules", "Add recurring rules for groom salary, regular suppliers, services, or other predictable payments."),
			],
		),
		(
			"Travel Manifest Basics",
			"Travel Manifest",
			[
				("trip_name", "Trip name", "Name the trip so match-day travel can be found quickly."),
				("status", "Status", "Track whether travel is planned, confirmed, in progress, completed, or cancelled."),
				("departure_date", "Departure and return", "Record departure and return dates so the owner calendar and match planning stay aligned."),
				("origin", "Origin", "Record where the horses leave from."),
				("destination", "Destination", "Record the match venue, tournament venue, or temporary stable."),
				("driver", "Driver", "Record who is responsible for transport."),
				("vehicle", "Vehicle", "Capture the lorry, trailer, or vehicle being used."),
				("horses", "Horses", "Add every horse travelling so the match team can verify the manifest."),
				("away_game_kit", "Away-game kit", "List equipment, feed, medicine, documents, and extras that must travel."),
				("notes", "Notes", "Use notes for timing, stabling instructions, loading issues, or owner context."),
			],
		),
		(
			"Horse Tack Configuration Basics",
			"Horse Tack Configuration",
			[
				("configuration_name", "Configuration name", "Name the setup in a way the groom can understand quickly."),
				("horse", "Horse", "Attach the configuration to the horse it belongs to."),
				("is_active", "Active setup", "Keep the current setup active and deactivate old setups rather than deleting history."),
				("saddle", "Saddle", "Record the saddle normally used for this horse."),
				("bit", "Bit", "Record the bit so match-day tack is consistent."),
				("bridle", "Bridle", "Capture bridle and related tack."),
				("boots", "Boots", "Record boots, bandages, and protective tack needed before work or play."),
				("prep_instructions", "Prep instructions", "Give the groom practical instructions for tacking up."),
				("sensitivity_notes", "Sensitivity notes", "Note rubbing, mouth sensitivity, girth sensitivity, or anything that changes handling."),
				("notes", "Notes", "Use notes for owner or trainer preference."),
			],
		),
		(
			"Match Day Basics",
			"Match Day",
			[
				("event_name", "Event name", "Name the polo game, tournament, or match day clearly."),
				("match_date", "Match date", "The date drives upcoming polo reports and dashboard cards."),
				("venue", "Venue", "Record where the match or tournament is taking place."),
				("status", "Status", "Track whether the match is planned, confirmed, completed, or cancelled."),
				("team", "Team", "Record your team or side for performance reporting."),
				("opponent", "Opponent", "Record the opposing team when known."),
				("number_of_chukkers", "Chukkers", "Set expected chukkers before assigning horses."),
				("chukkers", "Chukker assignments", "Assign horses and grooms to chukkers for match-day preparation."),
				("notes", "Notes", "Use notes for applications, logistics, result context, or follow-up details."),
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
	is_new = not frappe.db.exists("Module Onboarding", name)
	onboarding = get_or_new("Module Onboarding", name)
	onboarding.title = title
	onboarding.module = "Polomanagement"
	if is_new:
		onboarding.is_complete = 0
	onboarding.allow_roles = []
	for role in roles:
		onboarding.append("allow_roles", {"role": role})
	onboarding.steps = []
	for step in steps:
		onboarding.append("steps", {"step": step})
	if any(not int(frappe.db.get_value("Onboarding Step", step, "is_complete") or 0) for step in steps):
		onboarding.is_complete = 0
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
	is_new = not frappe.db.exists("Onboarding Step", title)
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
	if is_new:
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
