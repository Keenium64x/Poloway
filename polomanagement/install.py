import frappe


def after_migrate():
	setup_task_kanban()
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
				link("Horse Training Template", "DocType"),
			],
			"content": [
				content("shortcut", "Groom Dashboard", col=3),
				content("shortcut", "Owner Dashboard", col=3),
				content("shortcut", "Today Tasks", col=3),
				content("shortcut", "Horses", col=3),
				spacer(),
				content("card", "Daily Work", col=4),
				content("card", "Horse Records", col=4),
				content("card", "Planning", col=4),
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
				shortcut("Schedule Settings", "DocType", "Task Schedule Settings", icon="settings"),
				shortcut("Task Templates", "DocType", "Task Template", doc_view="List", icon="copy-check"),
				shortcut("Horses", "DocType", "Horse", doc_view="List", icon="heart-handshake"),
			],
			"links": [
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
				card("Setup"),
				link("Horse Feed Item", "DocType"),
				link("Horse Item Category", "DocType"),
				link("Horse Training Template", "DocType"),
			],
			"content": [
				content("shortcut", "Today Tasks", col=3),
				content("shortcut", "Schedule Settings", col=3),
				content("shortcut", "Task Templates", col=3),
				content("shortcut", "Horses", col=3),
				spacer(),
				content("card", "Planning", col=4),
				content("card", "Horse Oversight", col=4),
				content("card", "Setup", col=4),
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
		sidebar_link("Horse", "DocType", "Horse", icon="heart-handshake"),
		sidebar_section("Records"),
		sidebar_link("Horse Feeding Records", "Report", "Horse Feeding Records", child=1),
		sidebar_link("Horse Training Records", "Report", "Horse Training Records", child=1),
		sidebar_link("Horse Medical Records", "Report", "Horse Medical Records", child=1),
		sidebar_section("Planning"),
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
	workspace.roles = []

	for row in config["shortcuts"]:
		workspace.append("shortcuts", row)
	for row in config["links"]:
		workspace.append("links", row)
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
	key = "shortcut_name" if block_type == "shortcut" else "card_name"
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
