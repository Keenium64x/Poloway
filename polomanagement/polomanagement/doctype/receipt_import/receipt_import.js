frappe.ui.form.on("Receipt Import", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		const is_system_manager = frappe.user.has_role("System Manager");
		if (!is_system_manager) {
			hide_owner_receipt_fields(frm);
		}

		if (!frm.doc.transaction_input) {
			frm.add_custom_button(__("Process Receipt"), () => {
				run_receipt_method(frm, "process_receipt", (result) => {
					if (result.payment_record) {
						frappe.set_route("Form", "Payment Record", result.payment_record);
					} else if (result.transaction_input) {
						frappe.set_route("Form", "Transaction Input", result.transaction_input);
					}
				});
			}).addClass("btn-primary");
		}

		if (!is_system_manager) {
			return;
		}

		frm.add_custom_button(__("Add Files"), () => upload_files_to_receipt(frm), __("Receipt"));

		if (has_receipt_files(frm)) {
			frm.add_custom_button(__("Run OCR"), () => run_receipt_method(frm, "run_ocr"), __("Receipt"));
		}

		if (frm.doc.ocr_text) {
			frm.add_custom_button(__("Parse With AI"), () => run_receipt_method(frm, "parse_with_ai"), __("Receipt"));
		}

		if (!frm.doc.transaction_input && (frm.doc.lines || []).length) {
			frm.add_custom_button(__("Create Transaction Input"), () => {
				run_receipt_method(frm, "create_transaction_input", (name) => {
					frappe.set_route("Form", "Transaction Input", name);
				});
			}, __("Receipt"));
		}

		if (frm.doc.transaction_input) {
			frm.add_custom_button(__("Open Transaction Input"), () => {
				frappe.set_route("Form", "Transaction Input", frm.doc.transaction_input);
			}, __("Receipt"));
		}

		if (frm.doc.payment_record) {
			frm.add_custom_button(__("Open Payment Record"), () => {
				frappe.set_route("Form", "Payment Record", frm.doc.payment_record);
			}, __("Receipt"));
		}
	},
});

function has_receipt_files(frm) {
	return frm.doc.receipt_file || frm.doc.receipt_attachment || (frm.doc.receipt_files || []).length;
}

function hide_owner_receipt_fields(frm) {
	[
		"receipt_attachment",
		"receipt_file",
		"receipt_files",
		"extraction_section",
		"ocr_text",
		"extracted_json",
		"error_log",
		"parsed_details_section",
		"vendor_name",
		"vendor",
		"transaction_date",
		"transaction_type",
		"transaction_category",
		"currency",
		"payment_method",
		"total_amount",
		"ai_confidence",
		"lines_section",
		"lines",
		"notes_section",
		"notes",
	].forEach((fieldname) => {
		if (frm.fields_dict[fieldname]) {
			frm.set_df_property(fieldname, "hidden", 1);
		}
	});
}

function upload_files_to_receipt(frm) {
	const file_urls = [];
	let saved = false;
	const uploader = new frappe.ui.FileUploader({
		allow_multiple: true,
		dialog_title: __("Upload Receipt Files"),
		folder: "Home/Attachments",
		restrictions: {
			allowed_file_types: [".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"],
		},
		on_success(file_doc) {
			const file_url = file_doc.file_url || file_doc.name;
			if (file_url && !file_urls.includes(file_url)) {
				file_urls.push(file_url);
			}
		},
	});

	if (uploader.dialog) {
		uploader.dialog.$wrapper.on("hidden.bs.modal", () => {
			if (saved || !file_urls.length) {
				return;
			}
			saved = true;
			frappe.call({
				method: "polomanagement.polomanagement.doctype.receipt_import.receipt_import.add_receipt_files",
				args: {
					receipt_import: frm.doc.name,
					receipt_file_urls: JSON.stringify(file_urls),
				},
				freeze: true,
				freeze_message: __("Adding receipt files..."),
				callback() {
					frm.reload_doc();
				},
			});
		});
	}
}

function run_receipt_method(frm, method_name, callback) {
	frappe.call({
		method: `polomanagement.polomanagement.doctype.receipt_import.receipt_import.${method_name}`,
		args: { receipt_import: frm.doc.name },
		freeze: true,
		freeze_message: __("Processing receipt..."),
		callback(r) {
			frm.reload_doc();
			if (callback && r.message) {
				callback(r.message);
			}
		},
	});
}
