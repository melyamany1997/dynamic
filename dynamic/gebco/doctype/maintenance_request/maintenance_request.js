// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Maintenance Request', {
    refresh: function(frm) {
        frm.set_query('maintenance_contract', function(doc, cdt, cdn) {
            //var row = locals[cdt][cdn];
            return {
                "filters": {
                    "customer": frm.doc.company_name
                }
            };
        });
        if (frm.doc.docstatus == 1) {
            frm.add_custom_button(__("Create Maintenance Template"), function() {
                frappe.model.open_mapped_doc({
                    method: "dynamic.gebco.doctype.maintenance_request.maintenance_request.create_maintenance_request",
                    frm: frm,
                });
            });
        }
        frm.set_query('car', 'cars', function(doc, cdt, cdn) {
            //var row = locals[cdt][cdn];
            return {
                "filters": {
                    "customer": frm.doc.company_name
                }
            };
        });
    },
    //frm.set_query('cars')


});

frappe.ui.form.on('Cars Plate Numbers For Request', {
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

frappe.ui.form.on('Request Cars', {
    car: (frm, cdt, cdn) => {
        let row = locals[cdt][cdn]
            //console.log(row.plate_number)
        if (row.car.length > 0) {
            frappe.call({
                method: "check_cars_from_contract",
                doc: frm.doc,
                args: {
                    "car": row.car
                },
                callback(r) {
                    //console.log("rrrrrrrrrr", r)
                    if (r.message.exist == true) {
                        if (row.car.length > 1) {
                            let count = 0
                            for (let i = 0; i < frm.doc.cars.length; i++) {
                                if (frm.doc.cars[i].car == row.car) {

                                    count += 1
                                    if (count > 1) {
                                        row.car = ""
                                        frappe.msgprint("This Car Already Exist")
                                    }
                                }
                            }
                        }
                    } else {
                        row.car = ""
                        frappe.msgprint("This Car Doesnt Exist In contract")
                    }
                }
            })
        }

    }
})