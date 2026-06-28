import frappe
from frappe.desk.desktop import get_desktop_page as get_frappe_desktop_page
from frappe.desk.desktop import get_onboarding_data


@frappe.whitelist(methods=["GET"])
def get_desktop_page(page):
	workspace_data = get_frappe_desktop_page(page if isinstance(page, str) else frappe.as_json(page))
	add_native_onboardings(workspace_data, page)
	return workspace_data


def add_native_onboardings(workspace_data, page):
	if not isinstance(workspace_data, dict):
		return

	onboarding_names = get_onboarding_names(page)
	if not onboarding_names:
		return

	items = workspace_data.setdefault("onboardings", {}).setdefault("items", [])
	seen = {item.get("label") for item in items}
	for onboarding_name in onboarding_names:
		for onboarding in get_onboarding_data(onboarding_name) or []:
			if onboarding.get("label") not in seen:
				items.append(onboarding)
				seen.add(onboarding.get("label"))


def get_onboarding_names(page):
	page_data = frappe._dict(frappe.parse_json(page) or {})
	workspace_name = page_data.get("name") or page_data.get("title")
	if not workspace_name or not frappe.db.exists("Workspace", workspace_name):
		return []

	content = frappe.db.get_value("Workspace", workspace_name, "content")
	try:
		rows = frappe.parse_json(content) or []
	except Exception:
		rows = []

	return [
		row.get("data", {}).get("onboarding_name")
		for row in rows
		if row.get("type") == "onboarding" and row.get("data", {}).get("onboarding_name")
	]
