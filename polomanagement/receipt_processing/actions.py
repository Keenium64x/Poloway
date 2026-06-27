import json

import frappe
from frappe import _
from frappe.utils import flt, getdate


VALID_UNITS = {"kg", "g", "lb", "scoop", "flake", "bag", "ml", "l", "unit", "set", "pair"}
VALID_PAYMENT_METHODS = {"Cash", "Card", "Bank Transfer", "EFT", "Cheque", "Other"}
PAYMENT_METHOD_BY_LOWER = {method.lower(): method for method in VALID_PAYMENT_METHODS}


def apply_extraction_to_receipt(receipt_doc, extraction):
	data = extraction.model_dump() if hasattr(extraction, "model_dump") else dict(extraction)
	receipt_doc.extracted_json = json.dumps(data, indent=2, sort_keys=True)
	receipt_doc.vendor_name = data.get("vendor_name")
	receipt_doc.vendor = find_vendor(data.get("vendor_name"))
	receipt_doc.transaction_date = clean_date(data.get("transaction_date"))
	receipt_doc.transaction_type = data.get("transaction_type") or "Purchase"
	receipt_doc.transaction_category = data.get("transaction_category") or "Other"
	receipt_doc.currency = find_currency(data.get("currency"))
	receipt_doc.payment_method = clean_payment_method(data.get("payment_method"))
	receipt_doc.total_amount = flt(data.get("total_amount"))
	receipt_doc.ai_confidence = normalize_confidence(data.get("confidence"))
	receipt_doc.notes = data.get("notes")

	receipt_doc.set("lines", [])
	for row in data.get("lines") or []:
		total = flt(row.get("total"))
		quantity = flt(row.get("quantity")) or 1
		rate = flt(row.get("rate"))
		tax_amount = flt(row.get("tax_amount"))
		if not total and rate:
			total = quantity * rate + tax_amount
		if not rate and total:
			rate = max(total - tax_amount, 0) / quantity
		row["quantity"] = quantity
		row["rate"] = rate
		row["tax_amount"] = tax_amount
		row["total"] = total

		receipt_doc.append(
			"lines",
			{
				"line_type": clean_line_type(row.get("line_type")),
				"description": row.get("description"),
				"item_name": row.get("item_name"),
				"item": get_or_create_item_from_receipt_line(row, receipt_doc),
				"horse_name": row.get("horse_name"),
				"horse": find_horse(row.get("horse_name")) or receipt_doc.linked_horse,
				"groom_name": row.get("groom_name"),
				"groom_profile": find_groom(row.get("groom_name")),
				"tournament": row.get("tournament"),
				"reference_doctype": row.get("reference_doctype"),
				"reference_name": row.get("reference_name"),
				"quantity": quantity,
				"unit": clean_unit(row.get("unit")),
				"rate": rate,
				"tax_amount": tax_amount,
				"total": total,
				"cost_category": row.get("cost_category") or receipt_doc.transaction_category or "Other",
				"affects_inventory": 1 if row.get("affects_inventory") else 0,
				"confidence": normalize_confidence(row.get("confidence")),
			},
		)

	receipt_doc.status = "Ready"
	if not receipt_doc.lines and receipt_doc.total_amount:
		receipt_doc.append(
			"lines",
			{
				"line_type": "Other",
				"description": receipt_doc.vendor_name or _("Receipt total"),
				"horse": receipt_doc.linked_horse,
				"quantity": 1,
				"rate": receipt_doc.total_amount,
				"total": receipt_doc.total_amount,
				"cost_category": receipt_doc.transaction_category or "Other",
			},
		)

	return receipt_doc


def create_transaction_input_from_receipt(receipt_doc):
	if receipt_doc.transaction_input:
		return frappe.get_doc("Transaction Input", receipt_doc.transaction_input)
	if not receipt_doc.lines:
		frappe.throw(_("Review or add receipt lines before creating a transaction."))

	vendor = receipt_doc.vendor or create_vendor_if_needed(receipt_doc.vendor_name)
	transaction = frappe.new_doc("Transaction Input")
	transaction.transaction_type = receipt_doc.transaction_type or "Purchase"
	transaction.transaction_category = receipt_doc.transaction_category or "Other"
	transaction.transaction_date = receipt_doc.transaction_date or getdate()
	transaction.party_type = "Vendor" if vendor else "Other"
	transaction.vendor = vendor
	transaction.receipt_file = receipt_doc.receipt_file
	transaction.currency = receipt_doc.currency
	transaction.payment_method = receipt_doc.payment_method
	transaction.notes = build_transaction_notes(receipt_doc)

	for row in receipt_doc.lines:
		transaction.append(
			"lines",
			{
				"line_type": clean_line_type(row.line_type),
				"item": row.item,
				"horse": row.horse or receipt_doc.linked_horse,
				"groom_profile": row.groom_profile,
				"tournament": row.tournament,
				"reference_doctype": row.reference_doctype,
				"reference_name": row.reference_name,
				"description": row.description or row.item_name or row.horse_name or row.groom_name,
				"quantity": flt(row.quantity) or 1,
				"unit": clean_unit(row.unit),
				"rate": flt(row.rate),
				"tax_amount": flt(row.tax_amount),
				"cost_category": row.cost_category or receipt_doc.transaction_category or "Other",
				"affects_inventory": row.affects_inventory,
			},
		)

	transaction.insert(ignore_permissions=True)
	receipt_doc.db_set(
		{
			"transaction_input": transaction.name,
			"status": "Applied",
		}
	)
	return transaction


def submit_transaction_from_receipt(receipt_doc):
	transaction = create_transaction_input_from_receipt(receipt_doc)
	if transaction.docstatus == 0:
		transaction.submit()
	receipt_doc.db_set(
		{
			"transaction_input": transaction.name,
			"status": "Applied",
		}
	)
	return transaction


def resolve_file_from_attachment(file_url):
	if not file_url:
		return None
	if frappe.db.exists("File", file_url):
		return file_url
	file_name = frappe.db.get_value("File", {"file_url": file_url}, "name")
	if file_name:
		return file_name
	frappe.throw(_("Could not find uploaded file for {0}.").format(file_url))


def create_vendor_if_needed(vendor_name):
	if not vendor_name:
		return None
	existing = find_vendor(vendor_name)
	if existing:
		return existing
	vendor = frappe.new_doc("Vendor")
	vendor.vendor_name = vendor_name.strip()
	vendor.vendor_type = "Other"
	vendor.insert(ignore_permissions=True)
	return vendor.name


def find_vendor(vendor_name):
	return find_by_title("Vendor", "vendor_name", vendor_name)


def find_item(item_name):
	return find_by_title("Item", "item_name", item_name)


def get_or_create_item_from_receipt_line(row, receipt_doc):
	if clean_line_type(row.get("line_type")) != "Item":
		return None

	item_name = (row.get("item_name") or row.get("description") or "").strip()
	if not item_name:
		return None

	existing = find_item(item_name)
	if existing:
		return existing

	category = get_category_for_cost(row.get("cost_category") or receipt_doc.transaction_category)
	item = frappe.new_doc("Item")
	item.item_name = item_name[:140]
	item.item_category = category
	item.is_active = 1
	item.is_stock_item = 1 if row.get("affects_inventory") else 0
	item.description = row.get("description")
	item.default_unit = clean_unit(row.get("unit"))
	item.valuation_rate = flt(row.get("rate"))
	item.quantity_on_hand = 0
	item.insert(ignore_permissions=True)
	return item.name


def get_category_for_cost(cost_category):
	category_type_by_cost = {
		"Feed": "Food",
		"Equipment": "Equipment",
		"Supplies": "Stable Supply",
		"Supplements": "Supplement",
		"Medical": "Medical",
		"Farrier": "Service",
		"Groom Salary": "Service",
		"Overtime Pay": "Service",
		"Benefits": "Service",
		"Grooming": "Grooming",
	}
	preferred_names = {
		"Feed": "Food",
		"Equipment": "Horse Equipment",
		"Supplies": "Stable Supplies",
		"Supplements": "Supplements",
		"Medical": "Medical",
	}
	if preferred_names.get(cost_category) and frappe.db.exists("Item Category", preferred_names[cost_category]):
		return preferred_names[cost_category]
	category_type = category_type_by_cost.get(cost_category, "Other")
	category = frappe.db.get_value("Item Category", {"category_type": category_type, "is_group": 0}, "name")
	if category:
		return category
	category = frappe.db.get_value("Item Category", {"category_type": category_type}, "name")
	if category:
		return category
	return frappe.db.get_value("Item Category", {"item_category_name": "All Item Categories"}, "name") or "All Item Categories"


def find_horse(horse_name):
	if not horse_name:
		return None
	return find_by_title("Horse", "name1", horse_name) or find_by_title("Horse", "name", horse_name)


def find_groom(groom_name):
	if not groom_name:
		return None
	return find_by_title("Groom Profile", "groom_name", groom_name)


def find_currency(currency):
	if not currency:
		return None
	value = str(currency).strip().upper()
	if frappe.db.exists("Currency", value):
		return value
	return find_by_title("Currency", "currency_name", value)


def find_by_title(doctype, fieldname, value):
	if not value:
		return None
	value = str(value).strip()
	if not value:
		return None
	exact = frappe.db.get_value(doctype, {fieldname: value}, "name")
	if exact:
		return exact
	if frappe.db.exists(doctype, value):
		return value
	return frappe.db.get_value(doctype, {fieldname: ["like", f"%{value}%"]}, "name")


def clean_date(value):
	if not value:
		return None
	try:
		return getdate(value)
	except Exception:
		return None


def clean_line_type(value):
	return value if value in {"Item", "Horse", "Groom", "Tournament", "Service", "Other"} else "Other"


def clean_unit(value):
	if not value:
		return None
	unit = str(value).strip()
	return unit if unit in VALID_UNITS else None


def clean_payment_method(value):
	if not value:
		return None
	method = str(value).strip()
	return PAYMENT_METHOD_BY_LOWER.get(method.lower(), "Other")


def normalize_confidence(value):
	if value is None:
		return None
	score = flt(value)
	if score <= 1:
		return score * 100
	return score


def build_transaction_notes(receipt_doc):
	notes = []
	if receipt_doc.notes:
		notes.append(receipt_doc.notes)
	notes.append(_("Created from Receipt Import {0}.").format(receipt_doc.name))
	file_count = len([row for row in receipt_doc.receipt_files if row.receipt_file])
	if file_count > 1:
		notes.append(_("Receipt files processed: {0}.").format(file_count))
	if receipt_doc.ai_confidence is not None:
		notes.append(_("AI confidence: {0}").format(receipt_doc.ai_confidence))
	return "\n".join(notes)
