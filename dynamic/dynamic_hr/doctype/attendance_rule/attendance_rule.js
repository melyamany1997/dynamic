// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Rule', {
    // refresh: function(frm) {

    // }
    setup: function(frm) {
        frm.set_query('fingerprint_forgetten_penlaity_salary_component', function(doc) {
            return {
                filters: {
                    "type": 'Deduction',
                    "is_additional_salary":1
                }
            };
        });
         frm.set_query('fingerprint_forgetten_penlaity_salary_component', function(doc) {
            return {
                filters: {
                    "type": 'Deduction',
                    "is_additional_salary":1
                }
            };
        }); frm.set_query('hold_salary_component', function(doc) {
            return {
                filters: {
                    "type": 'Deduction',
                    "is_additional_salary":1
                }
            };
        });
        frm.set_query('salary_componat_for_late', function(doc) {
            return {
                filters: {
                    "type": 'Deduction',
                    "is_additional_salary":1
                }
            };
        });
        frm.set_query('salary_component_for_late_penalty', function(doc) {
            return {
                filters: {
                    "type": 'Deduction',
                    "is_additional_salary":1
                }
            };
        });
        frm.set_query('absent__component', function(doc) {
            return {
                filters: {
                    "type": 'Deduction',
                    "is_additional_salary":1
                }
            };
        });
        frm.set_query('additional_days_salary_component', function(doc) {
            return {
                filters: {
                    "type": 'Earning',
                    "is_additional_salary":1
                }
            };
        });
        frm.set_query('overtime_salary_component', function(doc) {
            return {
                filters: {
                    "type": 'Earning',
                    "is_additional_salary":1
                }
            };
        });
        frm.set_query('abset_penalty_component', function(doc) {
            return {
                filters: {
                    "type": 'Deduction',
                    "is_additional_salary":1
                }
            };
        }); 
        frm.set_query('less_time_penalty_salary_component', function(doc) {
            return {
                filters: {
                    "type": 'Deduction',
                    "is_additional_salary":1
                }
            };
        });
        frm.events.check_required(frm);
    },
    enable_permission_rule: function(frm) {
        frm.events.check_required(frm);
    },
    enable_late_penality: function(frm) {
        frm.events.check_required(frm);
    },
    enable_absent_penality: function(frm) {
        frm.events.check_required(frm);
    },
    enable_overtime: function(frm) {
        frm.events.check_required(frm);
    },
    enable_less_time_factor_penality: function(frm) {
        frm.events.check_required(frm);
    }, enable_less_time_penalty: function(frm) {
        frm.events.check_required(frm);
    },
    enable_fingerprint_penality: function(frm) {
        frm.events.check_required(frm);
    },
    daily_workers: function(frm) {
        frm.events.check_required(frm);
    },
    total_working_days_per_month: function(frm) {
         if (!frm.doc.total_working_days_per_month)
            return
        frm.events.calculate_total_working_hours_per_month(frm);
    },
    total_working_hours_per_day: function(frm) {
        if (!frm.doc.total_working_hours_per_day)
            return
        frm.events.calculate_total_working_hours_per_month(frm);
    },
    calculate_total_working_hours_per_month: function(frm) {
        let days = frm.doc.total_working_days_per_month || 0
        let hours_per_days = frm.doc.total_working_hours_per_day || 0
        frm.doc.total_working_hours_per_month = hours_per_days * days

        frm.refresh_field('total_working_hours_per_month')
    },
    check_required: function(frm) {
        // permission
        frm.toggle_reqd("max_permission_minutes", frm.doc.enable_permission_rule)
        frm.toggle_reqd("max_permissions_count", frm.doc.enable_permission_rule)
        frm.toggle_reqd("max_permission_minute_per_once", frm.doc.enable_permission_rule)

        //Late Rules
        frm.toggle_reqd("late_penalty_factor_by_date", frm.doc.enable_late_penality)
        // frm.toggle_reqd("salary_componat_for_late", frm.doc.enable_late_penality)
        // frm.toggle_reqd("salary_component_for_late_penalty", frm.doc.enable_late_penality)
        frm.toggle_reqd("caclulate_deduction_in_working_on_holiday", frm.doc.enable_late_penality)
        frm.toggle_reqd("caclulate_deduction_in_working_on_weekend", frm.doc.enable_late_penality)
        frm.toggle_reqd("late_role_table", frm.doc.enable_late_penality)

        // Absent Rule
        frm.toggle_reqd("absent_rules", frm.doc.enable_absent_penality)
        // frm.toggle_reqd("absent__component", frm.doc.enable_absent_penality)
        frm.toggle_reqd("absent_rate", frm.doc.enable_absent_penality)
        frm.toggle_reqd("abset_penalty_component", frm.doc.enable_absent_penality)


        // Overtime
        // frm.toggle_reqd("overtime_salary_component", frm.doc.enable_overtime)
            // frm.toggle_reqd("staying_up_late_salary_component",frm.doc.enable_overtime)
        frm.toggle_reqd("morning_overtime_start", frm.doc.enable_overtime)
        frm.toggle_reqd("evening_overtime_start", frm.doc.enable_overtime)
        frm.toggle_reqd("morning_overtime_factor", frm.doc.enable_overtime)
        frm.toggle_reqd("overtime_factor_in_weekend", frm.doc.enable_overtime)
        // frm.toggle_reqd("overtime_in_holiday_salary_component", frm.doc.enable_overtime)
        // frm.toggle_reqd("overtime_in_weekend_salary_component", frm.doc.enable_overtime)
        frm.toggle_reqd("morning_overtime_end", frm.doc.enable_overtime)
        frm.toggle_reqd("evening_overtime_end", frm.doc.enable_overtime)
        frm.toggle_reqd("evening_overtime_factor", frm.doc.enable_overtime)
            // frm.toggle_reqd("overtime_factor_in_holidays",frm.doc.enable_overtime)
        frm.toggle_reqd("deduct_overtime_from_delays", frm.doc.enable_overtime)
        frm.toggle_reqd("calculate_all_day_in_holiday", frm.doc.enable_overtime)
        frm.toggle_reqd("calculate_all_day_in_weekend", frm.doc.enable_overtime)


        // Less Time Setting
        // frm.toggle_reqd("less_time_salary_component", frm.doc.enable_less_time_factor_penality)
            // frm.toggle_reqd("less_rules",frm.doc.enable_less_time_factor_penality)
        frm.toggle_reqd("less_time_factor", frm.doc.enable_less_time_factor_penality)

        frm.toggle_reqd("less_time_penalty_factor", frm.doc.enable_less_time_factor_penality && frm.doc.enable_less_time_penalty )


        // FingerPrint Penality
        // frm.toggle_reqd("fingerprint_forgetten_penlaity_salary_component", frm.doc.enable_fingerprint_penality)
        frm.toggle_reqd("fingerprint_forgetten_in_penality", frm.doc.enable_fingerprint_penality)
        frm.toggle_reqd("fingerprint_forgetten_out_penality", frm.doc.enable_fingerprint_penality)


        frm.toggle_reqd("working_days", frm.doc.daily_workers)
        frm.toggle_reqd("against_weekend", frm.doc.daily_workers)




    }
});


frappe.ui.form.on('Late Attendance Componant Table', {
    // refresh: function(frm) {

    // }
    level_onefactor: function(frm, cdt, cdn) {

    },

    from_min: function(frm, cdt, cdn) {
        var loal = locals[cdt][cdn];
        var i = 0
        for (i = 1; i < frm.doc.late_role_table.length; i++) {


            if (frm.doc.late_role_table[i - 1].late_componant == frm.doc.late_role_table[i].late_componant) {
                frm.doc.late_role_table[i].late_componant = ""
                frm.doc.late_role_table[i].from_min = ""
                frm.doc.late_role_table[i].to_min = ""
                frm.refresh_filed("late_role_table")
                frappe.throw("You Dublicated Late Component")
            }

        }
        if (frm.doc.type == 'Daily') {
            for (i = 1; i < frm.doc.late_role_table.length; i++) {

                var to_min = frm.doc.late_role_table[i - 1].to_min
                if (frm.doc.late_role_table[i - 1].to_min > frm.doc.late_role_table[i].from_min) {
                    frm.doc.late_role_table[i].late_componant = ""
                    frm.doc.late_role_table[i].from_min = ""
                    frm.doc.late_role_table[i].to_min = ""

                    frappe.throw("Please Arange Times")
                }


            }


        }


    }
});