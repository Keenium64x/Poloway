import frappe
from frappe import _
from frappe.desk.doctype.kanban_board.kanban_board import (
	quick_kanban_board as frappe_quick_kanban_board,
	update_order_for_single_card as frappe_update_order_for_single_card,
)


@frappe.whitelist()
def update_order_for_single_card(
	board_name,
	docname,
	from_colname,
	to_colname,
	old_index,
	new_index,
	completion_notes=None,
	issue_reported=0,
	**kwargs,
):
	board = frappe.get_doc("Kanban Board", board_name)

	if board.reference_doctype != "Task" or board.field_name != "status":
		return frappe_update_order_for_single_card(
			board_name, docname, from_colname, to_colname, old_index, new_index
		)

	frappe.has_permission("Task", "write", throw=True)
	update_task_from_kanban(docname, to_colname, completion_notes, issue_reported)
	return board


def update_task_from_kanban(task_name, status, completion_notes=None, issue_reported=0):
	task = frappe.get_doc("Task", task_name)
	task.check_permission("write")

	if status == "Completed":
		task.complete(completion_notes=completion_notes, issue_reported=issue_reported)
		return

	task.status = status
	if status == "Open":
		task.progress = 0
		task.completed_on = None
		task.completed_by = None

	task.save(ignore_permissions=True)


@frappe.whitelist()
def quick_kanban_board(doctype, board_name, field_name, project=None):
	if doctype != "Task":
		return frappe_quick_kanban_board(doctype, board_name, field_name, project)

	from polomanagement.install import setup_task_kanban

	setup_task_kanban()
	return frappe.get_doc("Kanban Board", "Whiteboard")


def validate_single_task_kanban_board(doc, method=None):
	if doc.reference_doctype != "Task":
		return

	if doc.kanban_board_name != "Whiteboard":
		frappe.throw(_("Task Kanban is centralized. Use the Whiteboard board."))

	doc.field_name = "status"
	doc.private = 0
	doc.show_labels = 0
	doc.fields = frappe.as_json([])
	doc.filters = None
