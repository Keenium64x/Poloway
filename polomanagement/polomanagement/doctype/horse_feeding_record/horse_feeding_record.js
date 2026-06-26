frappe.ui.form.on("Horse Feeding Record", {
	setup(frm) {
		frm.set_query("item", () => ({
			query: "polomanagement.polomanagement.doctype.item.item.food_item_query",
		}));
	},
});
