frappe.query_reports["Horse Compliance Alerts"] = {
	filters: [
		{
			fieldname: "horse",
			label: __("Horse"),
			fieldtype: "Link",
			options: "Horse",
		},
		{
			fieldname: "record_type",
			label: __("Type"),
			fieldtype: "Select",
			options: "\nVaccination\nMedication\nTreatment\nInjury\nIllness\nDental\nFarrier\nTherapy\nProcedure\nObservation\nOther",
			default: "Vaccination",
		},
		{
			fieldname: "to_date",
			label: __("Due By"),
			fieldtype: "Date",
			default: frappe.datetime.add_days(frappe.datetime.get_today(), 30),
		},
		{
			fieldname: "only_open",
			label: __("Only Open"),
			fieldtype: "Check",
			default: 0,
		},
	],
};

