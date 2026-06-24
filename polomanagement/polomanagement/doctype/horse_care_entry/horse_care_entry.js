frappe.ui.form.on("Horse Care Entry", {
	setup(frm) {
		frm.set_query("feed_item", () => ({
			filters: {
				category: "Food",
				is_active: 1,
			},
		}));
	},

	refresh(frm) {
		if (frm.doc.linked_record_type && frm.doc.linked_record) {
			frm.add_custom_button(__("Open Record"), () => {
				frappe.set_route("Form", frm.doc.linked_record_type, frm.doc.linked_record);
			});
		}
	},
});
