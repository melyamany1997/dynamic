

frappe.query_reports["Mode Of Payment Report"] = {
    onload: function(report){
		if(frappe.query_report.get_filter_value('make_hidden') == 1)
        {
            $('[data-fieldname=mode_of_payment]').attr("disabled", true);
        }
	},
	"filters": [
		{
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        },

        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1,
            "width": "60px"
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1,
            "width": "60px"
        },
		{
            "fieldtype": "Break",
        },
		{
            "fieldname": "mode_of_payment",
            "label": __("Mode Of Payment"),
            "fieldtype": "Link",
            "options": "Mode of Payment",
            "reqd": 0
        },
        {
            "fieldname": "make_hidden",
            "label": __("make_hidden"),
            "fieldtype": "Select",
            "options": "0\n1",
            "default": "0",
            "hidden": "1",
            // on_change: function() {
            //     console.log("changed")
            //     console.log(frappe.query_report)
            //     // frappe.query_report.filters[3].readonly = 1
            //     $('[data-fieldname=mode_of_payment]').attr("disabled", true);
            //     frappe.query_report.refresh()
				
			// }
        },
		{
            "fieldname": "account_type",
            "label": __("Account Type"),
            "fieldtype": "Select",
            "options": "Cash\nBank",
            "default": "Cash",
            "reqd":0,
        },
        
	]
};



// if(frappe.query_report.get_filter_value('make_hidden') == 1){
//     $('[data-fieldname=mode_of_payment]').attr("disabled", true);
//     console.log("yeeeeeeeeeeeeees")


// }else{
//     console.log("not")

// }