import frappe
from frappe import _
from frappe.utils import flt, getdate, nowtime


def create_item_stock_ledger_entry(
	item,
	quantity_change,
	valuation_rate=None,
	movement_type="Stock Adjustment",
	voucher_type=None,
	voucher_no=None,
	voucher_detail_no=None,
	posting_date=None,
	inventory_location=None,
	remarks=None,
	reversed_against=None,
):
	item_doc = frappe.get_doc("Item", item)
	qty_change = flt(quantity_change)
	if not qty_change:
		return None

	quantity_after = flt(item_doc.quantity_on_hand) + qty_change
	if quantity_after < 0:
		frappe.throw(_("Item {0} does not have enough quantity on hand.").format(item_doc.item_name or item_doc.name))

	rate = flt(valuation_rate) or flt(item_doc.valuation_rate)
	if qty_change > 0 and flt(valuation_rate):
		item_doc.valuation_rate = flt(valuation_rate)
		rate = flt(valuation_rate)

	item_doc.quantity_on_hand = quantity_after
	item_doc.total_value = flt(item_doc.quantity_on_hand) * flt(item_doc.valuation_rate)
	item_doc.save(ignore_permissions=True)

	ledger = frappe.new_doc("Item Stock Ledger")
	ledger.posting_date = posting_date or getdate()
	ledger.posting_time = nowtime()
	ledger.item = item_doc.name
	ledger.inventory_location = inventory_location or item_doc.inventory_location
	ledger.movement_type = movement_type
	ledger.quantity_change = qty_change
	ledger.quantity_after = item_doc.quantity_on_hand
	ledger.valuation_rate = rate
	ledger.value_change = qty_change * rate
	ledger.value_after = item_doc.total_value
	ledger.voucher_type = voucher_type
	ledger.voucher_no = voucher_no
	ledger.voucher_detail_no = voucher_detail_no
	ledger.reversed_against = reversed_against
	ledger.remarks = remarks
	ledger.insert(ignore_permissions=True)
	return ledger.name


def reverse_stock_ledger_entries(voucher_type, voucher_no, posting_date=None):
	entries = frappe.get_all(
		"Item Stock Ledger",
		filters={
			"voucher_type": voucher_type,
			"voucher_no": voucher_no,
			"movement_type": ["!=", "Reversal"],
		},
		fields=["name", "item", "quantity_change", "valuation_rate", "inventory_location"],
		order_by="creation asc",
	)
	reversed_names = []
	for entry in entries:
		if frappe.db.exists("Item Stock Ledger", {"reversed_against": entry.name}):
			continue
		reversal = create_item_stock_ledger_entry(
			item=entry.item,
			quantity_change=flt(entry.quantity_change) * -1,
			valuation_rate=entry.valuation_rate,
			movement_type="Reversal",
			voucher_type=voucher_type,
			voucher_no=voucher_no,
			voucher_detail_no=entry.name,
			posting_date=posting_date or getdate(),
			inventory_location=entry.inventory_location,
			remarks=_("Reversal of {0}").format(entry.name),
			reversed_against=entry.name,
		)
		if reversal:
			reversed_names.append(reversal)
	return reversed_names
