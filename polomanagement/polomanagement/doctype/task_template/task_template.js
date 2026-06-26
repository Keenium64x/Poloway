frappe.ui.form.on("Task Template", {
	setup(frm) {
		frm.set_query("feed_item", "items", () => ({
			query: "polomanagement.polomanagement.doctype.item.item.food_item_query",
		}));
	},
});
