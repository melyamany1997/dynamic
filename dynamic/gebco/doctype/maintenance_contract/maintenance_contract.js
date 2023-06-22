// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Maintenance Contract', {
    refresh: function(frm) {
        if (frm.doc.docstatus == 1) {
            frm.add_custom_button(__("Renew"), function() {
                frappe.model.open_mapped_doc({
                    method: "dynamic.gebco.doctype.maintenance_contract.maintenance_contract.renew_contract",
                    frm: frm,
                });
            });
            if (frm.doc.sales_invoice == null || frm.doc.sales_invoice == '') {
                frm.add_custom_button(__("Create Sales Invoice"), function() {
                    frappe.model.open_mapped_doc({
                        method: "dynamic.gebco.doctype.maintenance_contract.maintenance_contract.create_sales_invoices",
                        frm: frm,
                    });
                });
            }
            if (frm.doc.status != "Completed") {
                frm.add_custom_button(__("Close"), function() {
                    frappe.call({
                        method: "update_doc_status",
                        doc: frm.doc,
                        callback(r) {
                            frm.reload_doc()
                        }
                    })
                });
            }
        }

        frm.set_query('plate_number', 'cars_plate_numbers', function(doc, cdt, cdn) {
            //var row = locals[cdt][cdn];
            return {
                "filters": {
                    "customer": frm.doc.customer
                }
            };
        });
        frm.set_query('cost_center', function(doc, cdt, cdn) {
            //var row = locals[cdt][cdn];
            return {
                "filters": {
                    "is_group": 0
                }
            };
        });
        frm.set_query('account', function(doc, cdt, cdn) {
            //var row = locals[cdt][cdn];
            return {
                "filters": {
                    "is_group": 0
                }
            };
        });

    },
    from_date: (frm) => {
        let from_date = frm.doc.from_date
        let to_date = frm.doc.to_date
        if (from_date != null && to_date != null) {
            if (to_date < from_date) {
                frm.set_value("from_date", "")
                frappe.msgprint("To date must be greate than to date")
            }
        }
    },
    to_date: (frm) => {
        let from_date = frm.doc.from_date
        let to_date = frm.doc.to_date
        if (from_date != null && to_date != null) {
            if (to_date < from_date) {
                frm.set_value("to_date", "")
                frappe.msgprint("To date must be greate than to date")
            }
        }
    },
    get_customer_cars: (frm) => {
        frappe.call({
            method: "get_customers_cars",
            doc: frm.doc,
            args: {
                "customer": frm.doc.customer
            },
            callback(r) {
                frm.refresh_fields("cars_plate_numbers")
            }
        })
    }
});

frappe.ui.form.on('Cars Plate Numbers', {
    plate_number: (frm, cdt, cdn) => {
        let row = locals[cdt][cdn]
        console.log(row.plate_number)
        if (row.plate_number.length > 1) {
            let count = 0
            for (let i = 0; i < frm.doc.cars_plate_numbers.length; i++) {
                if (frm.doc.cars_plate_numbers[i].plate_number == row.plate_number) {

                    count += 1
                    if (count > 1) {
                        row.plate_number = ""
                        frappe.msgprint("This Plate Number Already Exist")
                    }
                }
            }
        }
    }
})