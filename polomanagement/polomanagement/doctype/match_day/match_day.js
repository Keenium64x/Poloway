frappe.ui.form.on("Match Day", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		frm.add_custom_button(__("Open Match Board"), () => {
			frappe.route_options = {
				match_day: frm.doc.name,
				match_date: frm.doc.match_date,
			};
			frappe.set_route("query-report", "Match Day Board");
		});
	},
});
