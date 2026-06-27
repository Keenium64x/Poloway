import os

import frappe
from frappe import _


def parse_receipt_text(ocr_text):
	if not (ocr_text or "").strip():
		frappe.throw(_("Run OCR or enter receipt text before parsing with AI."))

	try:
		from pydantic_ai import Agent
	except ImportError:
		frappe.throw(
			_(
				"Receipt AI parsing needs pydantic-ai with the Google/Gemini provider. "
				"Install the app dependencies, then restart bench."
			)
		)

	from polomanagement.receipt_processing.schema import ReceiptExtraction

	api_key = frappe.conf.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY")
	if not api_key:
		frappe.throw(
			_(
				"Set a Gemini API key before parsing receipts. Use site config key gemini_api_key "
				"or environment variable GEMINI_API_KEY."
			)
		)

	os.environ["GOOGLE_API_KEY"] = api_key
	model = frappe.conf.get("receipt_ai_model") or os.environ.get("RECEIPT_AI_MODEL") or "google:gemini-2.5-flash"
	try:
		agent = Agent(model, output_type=ReceiptExtraction)
	except TypeError:
		agent = Agent(model, result_type=ReceiptExtraction)
	prompt = f"""
You extract structured bookkeeping data from OCR receipt text for a polo stable management system.

Rules:
- Return only fields in the provided schema.
- Use yyyy-mm-dd for transaction_date if the date is visible.
- If the receipt is a normal supplier receipt, transaction_type is Purchase.
- Choose the closest transaction_category from the schema.
- Split meaningful line items when possible.
- Use Item lines for physical goods, Horse lines for horse purchases/sales, Groom lines for groom salary/overtime/benefits,
  Tournament lines for entry fees/events, Service lines for labor/services, and Other when uncertain.
- Set affects_inventory true only for physical Item purchases/sales that should change stock.
- If you are uncertain, keep the value conservative and explain in notes.

OCR text:
{ocr_text}
"""
	result = agent.run_sync(prompt)
	extraction = getattr(result, "output", None) or getattr(result, "data", None)
	if not extraction:
		frappe.throw(_("The AI parser did not return receipt data."))
	return extraction
