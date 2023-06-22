from __future__ import unicode_literals

data = {

    'custom_fields': {
        'Additional Salary': [
            {
                "fieldname": "is_additional_salary",
                "fieldtype": "Check",
                "insert_after": "salary_component",
                "label": "Is Additional Salary",
                "read_only": 1,
                "hidden": 1,
                "fetch_from": "salary_component.is_additional_salary"

            },
            {
                "fieldname": "attendance_calculation",
                "fieldtype": "Link",
                "insert_after": "deduct_full_tax_on_selected_payroll_date",
                "label": "Attendance Calculation",
                "options": "Attendance Calculation",
                "read_only": 1,
            },
            {
                "fieldname": "attendance_flag",
                "fieldtype": "Data",
                "insert_after": "attendance_calculation",
                "label": "Attendance Flag",
                "read_only": 1,
                "hidden": 1,
                "translatable": 1,
            },
            {
                "fieldname": "salary_slips",
                "fieldtype": "Table MultiSelect",
                "insert_after": "attendance_flag",
                "label": "Salary Slips",
                "options": "Additional Salary Salary Slips",
                "read_only": 1,
                "allow_on_submit": 1,
                "depends_on": "eval:doc.is_recurring == 1"
            },
            {
                "fieldname": "penality",
                "fieldtype": "Check",
                "insert_after": "salary_slips",
                "label": "Penality",
                "default": 0,
                "read_only": 1
            },
            {
                "fieldname": "formula_section_break",
                "fieldtype": "Section Break",
                "insert_after": "overwrite_salary_structure_amount",
                "label": "Formula",
            },
            {
                "fieldname": "amount_based_on_formula",
                "fieldtype": "Check",
                "insert_after": "formula_section_break",
                "label": "Amount based on Formula",
                "fetch_from": "salary_component.amount_based_on_formula",
                "fetch_if_empty": 1,
                "allow_on_submit": 1
            },
            {
                "fieldname": "formula",
                "fieldtype": "Code",
                "insert_after": "amount_based_on_formula",
                "label": "Formula",
                "fetch_from": "salary_component.formula",
                "fetch_if_empty": 1,
                "depends_on": "eval:doc.amount_based_on_formula==1",
                "allow_on_submit": 1
            },
        ],
        'Salary Component': [
            {
                "fieldname": "is_additional_salary",
                "fieldtype": "Check",
                "insert_after": "column_break_4",
                "label": "Is Additional Salary"
            },
            {
                "fieldname": "consider_in_hour_rate",
                "fieldtype": "Check",
                "insert_after": "do_not_include_in_total",
                "label": "Consider In Hour Rate",
                "default": "1",
            },
        ],
        # 'Payroll Settings' : [
        #     {
        #         "fieldname": "absent_component",
        #         "fieldtype": "Link",
        #         "insert_after": "show_leave_balances_in_salary_slip",
        #         "options":"Salary Component",
        #         "label": "Absent Component",
        #     },
        # ],
        'Salary Structure Assignment': [
            {
                "fieldname": "absent_component",
                "fieldtype": "Link",
                "insert_after": "currency",
                "options": "Salary Component",
                "label": "Absent Component",
                "allow_on_submit": "1"
            },
            {
                "fieldname": "absent_deduction",
                "fieldtype": "Select",
                "insert_after": "absent_component",
                "options": "Absent Days\nPayment Days",
                "default" : "Absent Days" ,
                "label": "Absent Deduction depends on",
                "allow_on_submit": "1"
            },
        ],


    },
    "properties": [
        {
            "doctype": "Salary Structure Assignment",
            "doctype_or_field": "DocField",
            "fieldname": "base",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "1"
        },
        {
            "doctype": "Salary Structure Assignment",
            "doctype_or_field": "DocField",
            "fieldname": "variable",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "1"
        },
        {
            "doctype": "Salary Structure",
            "doctype_or_field": "DocField",
            "fieldname": "earnings",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "1"
        },
        {
            "doctype": "Salary Structure",
            "doctype_or_field": "DocField",
            "fieldname": "deductions",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "1"
        },
        {
            "doctype": "Salary Structure",
            "doctype_or_field": "DocField",
            "fieldname": "total_earning",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "1"
        },
        {
            "doctype": "Salary Structure",
            "doctype_or_field": "DocField",
            "fieldname": "total_deduction",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "1"
        },
        {
            "doctype": "Salary Structure",
            "doctype_or_field": "DocField",
            "fieldname": "net_pay",
            "property": "allow_on_submit",
            "property_type": "Check",
            "value": "1"
        },
    ],
    "property_setters": [

    ],
    'on_setup': 'dynamic.dynamic_payroll.setup.install_dynamic_payroll'
}
