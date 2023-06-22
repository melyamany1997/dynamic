// Copyright (c) 2016, Dynamic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Cheques Report"] = {
  filters: [
    {
      fieldname: "payment_type",
      label: __("Payment Type"),
      fieldtype: "Select",
      options: ["", "Pay", "Receive"],
      // depends_on: 'eval:doc.owner=="admin@admin.com"'
      // default: frappe.datetime.get_today(),
      // reqd: 1
    },
    {
      fieldname: "cheque_status",
      label: __("Cheque Status"),
      fieldtype: "Select",
      options: [
        "",
        "New",
        "Under Collect",
        "Rejected",
        "Rejected in Bank",
        "Collected",
        "Endorsed",
        "Paid",
      ],
    },
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
    },
    {
			"fieldname":"party_type",
			"label": __("Party Type"),
			"fieldtype": "Link",
			"options": "DocType",
			"get_query": function() {
				return {
					filters: {"name": ["in", ["Customer", "Supplier"]]}
				}
			},
      on_change: () => {
        frappe.query_report.set_filter_value("party", ' ');
				frappe.query_report.refresh();
      },
		},
    {
      fieldname: "party",
      label: __("Party"),
      fieldtype: "Dynamic Link",
      // options: "party_type",
      "get_options": function() {
				var applicant_type = frappe.query_report.get_filter_value('party_type');
				var applicant = frappe.query_report.get_filter_value('party');
				if(applicant && !applicant_type) {
					frappe.throw(__("Please select Party Type first"));
				}
				return applicant_type;
			}
    },  
    {
      fieldname: "bank",
      label: __("Bank"),
      fieldtype: "Link",
      options: "Bank",
    },
    {
      fieldname: "bank_account",
      label: __("Bank Account"),
      fieldtype: "Link",
      options: "Bank Account",
    },
  ],
};
