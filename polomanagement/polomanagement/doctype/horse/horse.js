// Copyright (c) 2026, Keenan Solomon and contributors
// For license information, please see license.txt

frappe.ui.form.on("Horse", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		const reports = [
			["Medical Records", "Horse Medical Records", "Horse Medical Record"],
			["Feeding Records", "Horse Feeding Records", "Horse Feeding Record"],
			["Training Records", "Horse Training Records", "Horse Training Record"],
		];

		reports.forEach(([label, _report, doctype]) => {
			frm.add_custom_button(__("New {0}", [label.slice(0, -1)]), () => {
				frappe.new_doc(doctype, { horse: frm.doc.name });
			}, __("Records"));
		});
	},

	medical_records_report(frm) {
		open_horse_report(frm, "Horse Medical Records");
	},

	feeding_records_report(frm) {
		open_horse_report(frm, "Horse Feeding Records");
	},

	training_records_report(frm) {
		open_horse_report(frm, "Horse Training Records");
	},
});

function open_horse_report(frm, report_name) {
	frappe.route_options = {
		horse: frm.doc.name,
	};
	frappe.set_route("query-report", report_name);
}
