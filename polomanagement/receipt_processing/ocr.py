import mimetypes
import shutil
import subprocess

import frappe
from frappe import _


SUPPORTED_IMAGE_EXTENSIONS = {".bmp", ".gif", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}


def extract_text_from_file(file_name):
	file_doc = frappe.get_doc("File", file_name)
	file_path = file_doc.get_full_path()
	extension = "." + file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""
	mimetype = mimetypes.guess_type(file_path)[0] or ""

	if extension not in SUPPORTED_IMAGE_EXTENSIONS and not mimetype.startswith("image/"):
		frappe.throw(_("Receipt OCR currently supports image files. Upload a photo or image file of the receipt."))

	text = extract_with_python_ocr(file_path) or extract_with_tesseract_cli(file_path)

	return (text or "").strip()


def extract_with_python_ocr(file_path):
	try:
		from PIL import Image
		import pytesseract
	except ImportError:
		return None

	try:
		with Image.open(file_path) as image:
			return pytesseract.image_to_string(image)
	except Exception:
		return None


def extract_with_tesseract_cli(file_path):
	if not shutil.which("tesseract"):
		frappe.throw(
			_(
				"Receipt OCR needs Tesseract. Install the tesseract-ocr system package, "
				"or install Pillow and pytesseract in the bench environment."
			)
		)

	try:
		result = subprocess.run(
			["tesseract", file_path, "stdout"],
			check=True,
			capture_output=True,
			text=True,
		)
	except Exception as exc:
		frappe.throw(_("Could not read receipt image with Tesseract OCR: {0}").format(exc))

	return result.stdout
