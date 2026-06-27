import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now


class ReceiptImport(Document):
	def validate(self):
		self.resolve_receipt_files()
		self.calculate_total_from_lines()

	def resolve_receipt_files(self):
		from polomanagement.receipt_processing.actions import resolve_file_from_attachment

		if self.receipt_attachment and not self.receipt_file:
			self.receipt_file = resolve_file_from_attachment(self.receipt_attachment)

		if self.receipt_file and not any(row.receipt_file == self.receipt_file for row in self.receipt_files):
			self.append(
				"receipt_files",
				{
					"receipt_attachment": self.receipt_attachment,
					"receipt_file": self.receipt_file,
					"status": "Uploaded",
				},
			)

		for row in self.receipt_files:
			if not row.receipt_file and row.receipt_attachment:
				row.receipt_file = resolve_file_from_attachment(row.receipt_attachment)
			if not row.status:
				row.status = "Uploaded"

		if not self.receipt_file and self.receipt_files:
			self.receipt_file = self.receipt_files[0].receipt_file
			self.receipt_attachment = self.receipt_files[0].receipt_attachment

	def calculate_total_from_lines(self):
		if self.lines:
			self.total_amount = sum((line.total or 0) for line in self.lines)

	def run_ocr(self):
		self.check_permission("write")
		self.resolve_receipt_files()
		file_rows = [row for row in self.receipt_files if row.receipt_file]
		if not file_rows:
			frappe.throw(_("Attach at least one receipt image before running OCR."))

		from polomanagement.receipt_processing.ocr import extract_text_from_file

		combined_text = []
		for row in file_rows:
			try:
				row.ocr_text = extract_text_from_file(row.receipt_file)
				row.status = "OCR Complete"
				row.error_log = None
				if row.ocr_text:
					combined_text.append(_("Receipt File {0}").format(row.idx))
					combined_text.append(row.ocr_text)
			except Exception:
				row.status = "Failed"
				row.error_log = frappe.get_traceback()
				raise

		self.ocr_text = "\n\n".join(combined_text)
		self.status = "OCR Complete"
		self.error_log = None
		self.save(ignore_permissions=True)
		return self.ocr_text

	def parse_with_ai(self):
		self.check_permission("write")
		if not self.ocr_text:
			self.run_ocr()

		from polomanagement.receipt_processing.actions import apply_extraction_to_receipt
		from polomanagement.receipt_processing.ai import parse_receipt_text

		try:
			extraction = parse_receipt_text(self.ocr_text)
			apply_extraction_to_receipt(self, extraction)
			self.error_log = None
			self.save(ignore_permissions=True)
		except Exception:
			self.status = "Failed"
			self.error_log = frappe.get_traceback()
			self.save(ignore_permissions=True)
			raise

		return self.name

	def create_transaction_input(self):
		self.check_permission("write")
		from polomanagement.receipt_processing.actions import create_transaction_input_from_receipt

		transaction = create_transaction_input_from_receipt(self)
		self.db_set(
			{
				"status": "Review Required",
				"review_status": "Pending",
			}
		)
		return transaction.name

	def process_receipt(self, post_payment=0):
		self.check_permission("write")
		if not self.ocr_text:
			self.run_ocr()
			self.reload()
		if not self.lines:
			self.parse_with_ai()
			self.reload()
		if post_payment or self.post_payment_immediately:
			return self.submit_transaction_from_receipt()

		transaction_name = self.create_transaction_input()
		return {"transaction_input": transaction_name}

	def submit_transaction_from_receipt(self):
		self.check_permission("write")
		from polomanagement.receipt_processing.actions import submit_transaction_from_receipt

		transaction = submit_transaction_from_receipt(self)
		self.mark_posted()
		return {"transaction_input": transaction.name}

	def post_payment_from_receipt(self):
		return self.submit_transaction_from_receipt()

	def mark_posted(self):
		self.db_set(
			{
				"review_status": "Posted",
				"reviewed_by": frappe.session.user,
				"reviewed_on": now(),
				"status": "Posted",
			}
		)

	def mark_reviewed(self, review_notes=None):
		self.check_permission("write")
		self.db_set(
			{
				"review_status": "Reviewed",
				"reviewed_by": frappe.session.user,
				"reviewed_on": now(),
				"review_notes": review_notes,
			}
		)
		return self.name


@frappe.whitelist()
def run_ocr(receipt_import):
	doc = frappe.get_doc("Receipt Import", receipt_import)
	doc.run_ocr()
	return doc.name


@frappe.whitelist()
def parse_with_ai(receipt_import):
	doc = frappe.get_doc("Receipt Import", receipt_import)
	return doc.parse_with_ai()


@frappe.whitelist()
def create_transaction_input(receipt_import):
	doc = frappe.get_doc("Receipt Import", receipt_import)
	return doc.create_transaction_input()


@frappe.whitelist()
def process_receipt(receipt_import, post_payment=0):
	doc = frappe.get_doc("Receipt Import", receipt_import)
	return doc.process_receipt(post_payment=post_payment)


@frappe.whitelist()
def submit_transaction_from_receipt(receipt_import):
	doc = frappe.get_doc("Receipt Import", receipt_import)
	result = doc.submit_transaction_from_receipt()
	doc.mark_posted()
	return result


@frappe.whitelist()
def post_payment_from_receipt(receipt_import):
	return submit_transaction_from_receipt(receipt_import)


@frappe.whitelist()
def mark_reviewed(receipt_import, review_notes=None):
	doc = frappe.get_doc("Receipt Import", receipt_import)
	return doc.mark_reviewed(review_notes=review_notes)


@frappe.whitelist()
def add_receipt_files(receipt_import, receipt_file_urls):
	ensure_receipt_import_user()
	doc = frappe.get_doc("Receipt Import", receipt_import)
	doc.check_permission("write")
	for file_url in normalize_file_urls(receipt_file_urls=receipt_file_urls):
		if not any(row.receipt_attachment == file_url for row in doc.receipt_files):
			doc.append("receipt_files", {"receipt_attachment": file_url, "status": "Uploaded"})
	doc.save(ignore_permissions=True)
	return doc.name


@frappe.whitelist()
def create_receipt_import(receipt_file_url=None, receipt_file_urls=None, linked_horse=None, process=0, post_payment=0):
	ensure_receipt_import_user()
	file_urls = normalize_file_urls(receipt_file_url, receipt_file_urls)
	doc = frappe.new_doc("Receipt Import")
	if file_urls:
		doc.receipt_attachment = file_urls[0]
		for file_url in file_urls:
			doc.append("receipt_files", {"receipt_attachment": file_url, "status": "Uploaded"})
	doc.linked_horse = linked_horse
	doc.status = "Uploaded"
	doc.insert(ignore_permissions=True)
	if process:
		result = doc.process_receipt(post_payment=post_payment)
		result["receipt_import"] = doc.name
		return result
	return doc.name


def normalize_file_urls(receipt_file_url=None, receipt_file_urls=None):
	if isinstance(receipt_file_urls, str):
		try:
			receipt_file_urls = frappe.parse_json(receipt_file_urls)
		except Exception:
			receipt_file_urls = [receipt_file_urls]
	file_urls = []
	if receipt_file_url:
		file_urls.append(receipt_file_url)
	for file_url in receipt_file_urls or []:
		if file_url and file_url not in file_urls:
			file_urls.append(file_url)
	return file_urls


def ensure_receipt_import_user():
	if frappe.session.user == "Administrator":
		return
	if "System Manager" in frappe.get_roles() or "Horse Owner" in frappe.get_roles():
		return
	frappe.throw(_("Only a Horse Owner or System Manager can upload receipts."))
