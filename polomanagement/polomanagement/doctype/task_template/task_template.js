frappe.ui.form.on("Task Template", {
	setup(frm) {
		frm.set_query("feed_item", "items", () => ({
			filters: {
				category: "Food",
				is_active: 1,
			},
		}));
	},
});
