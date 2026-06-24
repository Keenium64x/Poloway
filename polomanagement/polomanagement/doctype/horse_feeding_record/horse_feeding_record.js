frappe.ui.form.on("Horse Feeding Record", {
	setup(frm) {
		frm.set_query("item", () => ({
			filters: {
				category: "Food",
				is_active: 1,
			},
		}));
	},
});
