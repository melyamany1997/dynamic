// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Maintenance Template', {
    refresh: function(frm) {

        if (frm.doc.docstatus == 1) {
            if (frm.doc.include_spare_part == "YES" && (frm.doc.stock_entry == null || frm.doc.stock_entry == "")) {
                frm.add_custom_button(__("Create Stock Entry"), function() {
                    //console.log("asd", frm.doc.items)
                    if (frm.doc.items.length == 0) {
                        frappe.throw("You Dont Have Items")
                    }
                    frappe.call({
                        method: "create_stock_entrys",
                        doc: frm.doc,
                        callback(r) {
                            frm.reload_doc()
                        }
                    })
                });
            } else if (frm.doc.include_spare_part == "NO" || !frm.doc.maintenance_contract) {
                if ((frm.doc.delivery_note == '' || frm.doc.delivery_note == undefined) && frm.doc.sales_invoicec != '') {
                    frm.add_custom_button(__("Create Delivery Note"), function() {
                        frappe.model.open_mapped_doc({
                            method: "dynamic.gebco.doctype.maintenance_template.maintenance_template.create_delivery_note",
                            frm: frm,
                        });
                    });
                }
                if (frm.doc.sales_invoice == '' || frm.doc.sales_invoice == undefined) {
                    frm.add_custom_button(__("Create Sales Invoice"), function() {
                        frappe.model.open_mapped_doc({
                            method: "dynamic.gebco.doctype.maintenance_template.maintenance_template.create_sales_invoice",
                            frm: frm,
                        });
                    });
                }
            }
        }
        frm.set_query('item', 'service_items', function(doc, cdt, cdn) {
            //var row = locals[cdt][cdn];
            return {
                "filters": {
                    "is_stock_item": false
                }
            };
        });
        frm.set_query('item', 'items', function(doc, cdt, cdn) {
            //var row = locals[cdt][cdn];
            return {
                "filters": {
                    "is_stock_item": true
                }
            };
        });
        frm.set_query('maintenance_contract', function(doc, cdt, cdn) {
            //var row = locals[cdt][cdn];
            return {
                "filters": {
                    "docstatus": 1
                }
            };
        });
    }
});

frappe.ui.form.on('Cars Plate Numbers For Template', {
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

frappe.ui.form.on('Template Cars', {
    car: (frm, cdt, cdn) => {
        let row = locals[cdt][cdn]
            //console.log(row.plate_number)
        frappe.call({
            method: "check_cars_from_contract",
            doc: frm.doc,
            args: {
                "car": row.car
            },
            callback(r) {
                console.log("rrrrrrrrrr", r)
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
})

frappe.ui.form.on('Maintenance Team', {
    employee: (frm, cdt, cdn) => {
        let row = locals[cdt][cdn]
        let employees = frm.doc.maintenance_team
        let count = 0
        for (let i = 0; i < employees.length; i++) {
            if (employees[i].employee == row.employee) {
                count += 1
                if (count > 1) {
                    row.employee = ""
                    frappe.msgprint("This Employee Already Exist")
                }
            }
        }
    }
})

frappe.ui.form.on('Maintenance Template Items', {
    item: (frm, cdt, cdn) => {
        let row = locals[cdt][cdn]
        if (row.item.length > 0) {
            frappe.call({
                method: "get_item_price",
                doc: frm.doc,
                args: {
                    "item_code": row.item
                },
                callback(r) {
                    if (r.message) {
                        row.price = r.message
                        frm.refresh_fields("items")
                    }
                }
            })
        }
    },
    qty: (frm, cdt, cdn) => {
        let row = locals[cdt][cdn]
        let qty = row.qty
        let rate = row.price
        let total = qty * rate
        row.amount = total
        frm.refresh_fields("items")
    },
    amount: (frm, cdt, cdn) => {
        let row = locals[cdt][cdn]
        let qty = row.qty
        let rate = row.price
        let total = qty * rate
        row.amount = total
        frm.refresh_fields("items")
    },
})

frappe.ui.form.on('Maintenance Template Service Items', {
    item: (frm, cdt, cdn) => {
        let row = locals[cdt][cdn]
        if (row.item.length > 0) {
            frappe.call({
                method: "get_item_price",
                doc: frm.doc,
                args: {
                    "item_code": row.item
                },
                callback(r) {
                    if (r.message) {
                        row.price = r.message
                        frm.refresh_fields("service_items")
                    }
                }
            })
        }
    },
    qty: (frm, cdt, cdn) => {
        let row = locals[cdt][cdn]
        let qty = row.qty
        let rate = row.price
        let total = qty * rate
        row.amount = total
        frm.refresh_fields("service_items")
    },
    amount: (frm, cdt, cdn) => {
        let row = locals[cdt][cdn]
        let qty = row.qty
        let rate = row.price
        let total = qty * rate
        row.amount = total
        frm.refresh_fields("service_items")

    },
})