frappe.query_reports["Match Day Board"] = {
	filters: [
		{
			fieldname: "match_day",
			label: __("Match Day"),
			fieldtype: "Link",
			options: "Match Day",
		},
		{
			fieldname: "match_date",
			label: __("Match Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "horse",
			label: __("Horse"),
			fieldtype: "Link",
			options: "Horse",
		},
		{
			fieldname: "assignment_status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nPlanned\nTack Up\nWarm Up\nPlaying\nCool Down\nDone",
		},
	],
};

