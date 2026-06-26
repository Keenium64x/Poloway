import frappe


def after_migrate():
	setup_task_kanban()
	setup_inventory()
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
	setup_workspaces()
	setup_workspace_sidebar()
	setup_desktop_icon()


def setup_workspaces():
	upsert_workspace(
		"Polomanagement",
		{
			"title": "Polomanagement",
			"icon": "flag",
			"indicator_color": "blue",
			"roles": [],
			"shortcuts": [
				url_shortcut("Groom Dashboard", "/app/groom-dashboard", icon="list-todo"),
				url_shortcut("Owner Dashboard", "/app/owner-dashboard", icon="layout-dashboard"),
				task_whiteboard_shortcut(),
				shortcut("Owner Calendar", "DocType", "Owner Task", doc_view="Calendar", icon="calendar-days"),
				url_shortcut("Upload Receipt", "/app/owner-dashboard?upload_receipt=1", icon="receipt-text"),
				shortcut("Horses", "DocType", "Horse", doc_view="List", icon="heart-handshake"),
			],
			"links": [
				card("Daily Work"),
				link("Task", "DocType"),
				link("Horse Care Entry", "DocType"),
				card("Horse Records"),
				link("Horse", "DocType"),
				link("Horse Feeding Record", "DocType"),
				link("Horse Training Record", "DocType"),
				link("Horse Medical Record", "DocType"),
				card("Planning"),
				link("Task Template", "DocType"),
				link("Task Schedule Settings", "DocType"),
				link("Owner Task", "DocType"),
				link("Horse Training Template", "DocType"),
				card("Inventory"),
				link("Item", "DocType"),
				link("Item Category", "DocType"),
				link("Inventory Location", "DocType"),
				card("Money"),
				link("Vendor", "DocType"),
				link("Purchase", "DocType"),
				link("Vendor Quote", "DocType"),
				link("Receipt Import", "DocType"),
				link("Transaction Input", "DocType"),
				link("Payment Record", "DocType"),
				link("Financial Overview", "Report"),
				link("Payment Records", "Report"),
				link("Quote Comparison", "Report"),
				link("Horse Expenses", "Report"),
				link("Item Cost History", "Report"),
				link("Unposted Transactions", "Report"),
			],
			"number_cards": [],
			"content": [
				content("shortcut", "Groom Dashboard", col=3),
				content("shortcut", "Owner Dashboard", col=3),
				content("shortcut", "Today Tasks", col=3),
				content("shortcut", "Owner Calendar", col=3),
				content("shortcut", "Horses", col=3),
				spacer(),
				content("card", "Daily Work", col=4),
				content("card", "Horse Records", col=4),
				content("card", "Planning", col=4),
				content("card", "Inventory", col=4),
				content("card", "Money", col=4),
			],
		},
	)

	upsert_workspace(
		"Groom Dashboard",
		{
			"title": "Groom Dashboard",
			"icon": "list-todo",
			"indicator_color": "green",
			"parent_page": "Polomanagement",
			"roles": ["Horse Groom", "Stable Manager", "System Manager"],
			"shortcuts": [
				task_whiteboard_shortcut(),
				shortcut("Task List", "DocType", "Task", doc_view="List", icon="list"),
				shortcut("Task Calendar", "DocType", "Task", doc_view="Calendar", icon="calendar-days"),
				shortcut("Horse Care Entry", "DocType", "Horse Care Entry", doc_view="New", icon="clipboard-plus"),
			],
			"links": [
				card("My Work"),
				link("Task", "DocType"),
				link("Horse Care Entry", "DocType"),
				card("Records"),
				link("Horse Feeding Record", "DocType"),
				link("Horse Training Record", "DocType"),
				link("Horse Medical Record", "DocType"),
				link("Horse", "DocType"),
			],
			"number_cards": [],
			"content": [
				content("shortcut", "Today Tasks", col=3),
				content("shortcut", "Task List", col=3),
				content("shortcut", "Task Calendar", col=3),
				content("shortcut", "Horse Care Entry", col=3),
				spacer(),
				content("card", "My Work", col=6),
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
			"parent_page": "Polomanagement",
			"roles": ["Horse Owner", "Stable Manager", "System Manager"],
			"shortcuts": [
				task_whiteboard_shortcut(),
				shortcut("Owner Calendar", "DocType", "Owner Task", doc_view="Calendar", icon="calendar-days"),
				url_shortcut("Owner Gantt", "/app/owner-task/view/gantt", icon="gantt-chart"),
				shortcut("Issues", "Report", "Owner Task Issues", icon="circle-alert"),
				shortcut("Schedule Settings", "DocType", "Task Schedule Settings", icon="settings"),
				shortcut("Task Templates", "DocType", "Task Template", doc_view="List", icon="copy-check"),
				shortcut("Horses", "DocType", "Horse", doc_view="List", icon="heart-handshake"),
				shortcut("Payments", "Report", "Payment Records", icon="circle-dollar-sign"),
				url_shortcut("Upload Receipt", "/app/owner-dashboard?upload_receipt=1", icon="receipt-text"),
				shortcut("Purchases", "DocType", "Purchase", doc_view="List", icon="shopping-cart"),
				shortcut("Financial Overview", "Report", "Financial Overview", icon="chart-column"),
				shortcut("Receipt Imports", "DocType", "Receipt Import", doc_view="List", icon="receipt-text"),
				shortcut("Quotes", "Report", "Quote Comparison", icon="scale"),
				shortcut("Horse Expenses", "Report", "Horse Expenses", icon="chart-column"),
				shortcut("Unposted", "Report", "Unposted Transactions", icon="file-clock"),
			],
			"links": [
				card("Owner Actions"),
				link("Owner Task", "DocType"),
				link("Owner Task Issues", "Report"),
				card("Planning"),
				link("Task Schedule Settings", "DocType"),
				link("Task Template", "DocType"),
				link("Task", "DocType"),
				card("Horse Oversight"),
				link("Horse", "DocType"),
				link("Horse Owner", "DocType"),
				link("Horse Feeding Records", "Report"),
				link("Horse Training Records", "Report"),
				link("Horse Medical Records", "Report"),
				card("Money"),
				link("Purchase", "DocType"),
				link("Financial Overview", "Report"),
				link("Payment Records", "Report"),
				link("Receipt Import", "DocType"),
				link("Quote Comparison", "Report"),
				link("Horse Expenses", "Report"),
				link("Item Cost History", "Report"),
				link("Unposted Transactions", "Report"),
				link("Transaction Input", "DocType"),
				link("Vendor Quote", "DocType"),
				link("Vendor", "DocType"),
				card("Setup"),
				link("Item", "DocType"),
				link("Item Category", "DocType"),
				link("Inventory Location", "DocType"),
				link("Horse Training Template", "DocType"),
			],
			"number_cards": [],
			"content": [
				content("shortcut", "Today Tasks", col=3),
				content("shortcut", "Owner Calendar", col=3),
				content("shortcut", "Owner Gantt", col=3),
				content("shortcut", "Issues", col=3),
				content("shortcut", "Horses", col=3),
				content("shortcut", "Upload Receipt", col=3),
				content("shortcut", "Purchases", col=3),
				content("shortcut", "Financial Overview", col=3),
				content("shortcut", "Payments", col=3),
				content("shortcut", "Receipt Imports", col=3),
				content("shortcut", "Quotes", col=3),
				content("shortcut", "Horse Expenses", col=3),
				content("shortcut", "Unposted", col=3),
				spacer(),
				content("card", "Owner Actions", col=4),
				content("card", "Horse Oversight", col=4),
				content("card", "Planning", col=4),
				content("card", "Money", col=4),
			],
		},
	)


def setup_workspace_sidebar():
	sidebar = get_or_new("Workspace Sidebar", "Polomanagement")
	sidebar.title = "Polomanagement"
	sidebar.header_icon = "flag"
	sidebar.module = "Polomanagement"
	sidebar.app = "polomanagement"
	sidebar.standard = 1
	sidebar.items = []

	for item in [
		sidebar_link("Home", "Workspace", "Polomanagement", icon="home"),
		sidebar_link("Groom Dashboard", "Workspace", "Groom Dashboard", icon="list-todo"),
		sidebar_link("Owner Dashboard", "Workspace", "Owner Dashboard", icon="layout-dashboard"),
		sidebar_url("Task", "/app/task/view/kanban/Whiteboard", icon="list"),
		sidebar_link("Owner Calendar", "DocType", "Owner Task", icon="calendar-days"),
		sidebar_link("Issues", "Report", "Owner Task Issues", icon="circle-alert"),
		sidebar_link("Horse", "DocType", "Horse", icon="heart-handshake"),
		sidebar_section("Records"),
		sidebar_link("Horse Feeding Records", "Report", "Horse Feeding Records", child=1),
		sidebar_link("Horse Training Records", "Report", "Horse Training Records", child=1),
		sidebar_link("Horse Medical Records", "Report", "Horse Medical Records", child=1),
		sidebar_section("Inventory"),
		sidebar_link("Item", "DocType", "Item", child=1),
		sidebar_link("Item Category", "DocType", "Item Category", child=1),
		sidebar_link("Inventory Location", "DocType", "Inventory Location", child=1),
		sidebar_section("Money"),
		sidebar_link("Financial Overview", "Report", "Financial Overview", child=1),
		sidebar_link("Payment Records", "Report", "Payment Records", child=1),
		sidebar_link("Purchase", "DocType", "Purchase", child=1),
		sidebar_link("Quote Comparison", "Report", "Quote Comparison", child=1),
		sidebar_link("Horse Expenses", "Report", "Horse Expenses", child=1),
		sidebar_link("Item Cost History", "Report", "Item Cost History", child=1),
		sidebar_link("Unposted Transactions", "Report", "Unposted Transactions", child=1),
		sidebar_link("Receipt Import", "DocType", "Receipt Import", child=1),
		sidebar_link("Transaction Input", "DocType", "Transaction Input", child=1),
		sidebar_link("Vendor Quote", "DocType", "Vendor Quote", child=1),
		sidebar_link("Vendor", "DocType", "Vendor", child=1),
		sidebar_section("Planning"),
		sidebar_link("Owner Task", "DocType", "Owner Task", child=1),
		sidebar_link("Task Template", "DocType", "Task Template", child=1),
		sidebar_link("Task Schedule Settings", "DocType", "Task Schedule Settings", child=1),
	]:
		sidebar.append("items", item)

	sidebar.save(ignore_permissions=True)


def setup_desktop_icon():
	icon = get_or_new("Desktop Icon", "Polomanagement")
	icon.label = "Polomanagement"
	icon.icon_type = "Link"
	icon.link_type = "Workspace Sidebar"
	icon.link_to = "Polomanagement"
	icon.sidebar = "Polomanagement"
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
	workspace.roles = []

	for row in config["shortcuts"]:
		workspace.append("shortcuts", row)
	for row in config["links"]:
		workspace.append("links", row)
	for row in config.get("number_cards", []):
		workspace.append("number_cards", row)
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
		("Medical", "Medical", "All Item Categories", "Medical Cabinet", "unit", "Veterinarian", 1),
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
