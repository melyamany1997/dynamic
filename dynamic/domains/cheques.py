from __future__ import unicode_literals
from ntpath import join

cheque_status = [
    "New",
    "Under Collect",
    "Collected",
    "Endorsed",
    "Cash",
    "Paid",
    "Rejected in Bank",
    "Rejected",
    "Return"
]
data = {
    'custom_fields': {
        'Company': [
            {
                "fieldname": "cheques_section",
                "fieldtype": "Section Break",
                "insert_after": "asset_received_but_not_billed",
                "label": "Cheques Setting",
            },
            {
                "fieldname": "incoming_cheque_wallet_account",
                "fieldtype": "Link",
                "insert_after": "cheques_section",
                "label": "Incoming Cheques Wallet Account",
                "options": "Account"
            },
            {
                "fieldname": "outcoming_cheque_wallet_account",
                "fieldtype": "Link",
                "insert_after": "incoming_cheque_wallet_account",
                "label": "Outcoming Cheques Wallet Account",
                "options": "Account"
            },
            {
                "fieldname": "rejected_cheques_bank_account",
                "fieldtype": "Link",
                "insert_after": "outcoming_cheque_wallet_account",
                "label": "Rejected Cheques Bank Account",
                "options": "Account"
            },
            {
                "fieldname": "cheques_column",
                "fieldtype": "Column Break",
                "insert_after": "rejected_cheques_bank_account",
                "label": "",
            },
            {
                "fieldname": "returned_cheques_bank_account",
                "fieldtype": "Link",
                "insert_after": "cheques_column",
                "label": "Returned Cheques Bank Account",
                "options": "Account"
            },
            {
                "fieldname": "deposit_cheques_bank_account",
                "fieldtype": "Link",
                "insert_after": "returned_cheques_bank_account",
                "label": "Deposit Cheques Bank Account",
                "options": "Account"
            },
            {
                "fieldname": "bank_expenses_account",
                "fieldtype": "Link",
                "insert_after": "returned_cheques_bank_account",
                "label": "Bank Expenses Account",
                "options": "Account"
            },
            {
                "fieldname": "cheque_submit",
                "fieldtype": "Check",
                "insert_after": "bank_expenses_account",
                "label": "Cheque Submit",
                "default":0
            }
        ],
        'Bank Account': [
            {
                "fieldname": "cheques_section",
                "fieldtype": "Section Break",
                "insert_after": "company",
                "label": "Cheques Section",
            },
            {
                "fieldname": "cheques_payable_account",
                "fieldtype": "Link",
                "insert_after": "cheques_section",
                "label": "Cheques Payable Account",
                "options": "Account",
                "reqd": 1
            },
            {
                "fieldname": "cheques_column",
                "fieldtype": "Column Break",
                "insert_after": "cheques_payable_account",
                "label": "",
            },
            {
                "fieldname": "cheques_receivable_account",
                "fieldtype": "Link",
                "insert_after": "cheques_column",
                "label": "Cheques Receivable Account",
                "options": "Account",
                "reqd": 1
            },
            # Commissions Section
            {
                "fieldname": "cheques_commission_section",
                "fieldtype": "Section Break",
                "insert_after": "cheques_receivable_account",
                "label": "Commissions",
            },
            # {
            #     "fieldname": "bank_guarantee_column1",
            #     "fieldtype": "Column Break",
            #     "insert_after": "cheques_commission_section",
            #     "label": "Bank Guarantee",
            # },
            # {
            #     "fieldname": "bank_warranty_letter_commission",
            #     "fieldtype": "Float",
            #     "insert_after": "bank_guarantee_column1",
            #     "label": "Bank Warranty Letter Commission",
            #     "default": 0
            # },
            # {
            #     "fieldname": "initial_bank_warranty_letter_commission",
            #     "fieldtype": "Percent",
            #     "insert_after": "bank_warranty_letter_commission",
            #     "label": "Initial Bank Warranty Letter Commission",
            #     "default": 0
            # },
            # {
            #     "fieldname": "bank_warranty_letter_commission_advance_payment",
            #     "fieldtype": "Percent",
            #     "insert_after": "initial_bank_warranty_letter_commission",
            #     "label": "Bank Warranty Letter Commission Advance Payment",
            #     "default": 0
            # },
            # {
            #     "fieldname": "bank_warranty_letter_reservation_commission_advance_payment",
            #     "fieldtype": "Percent",
            #     "insert_after": "bank_warranty_letter_commission_advance_payment",
            #     "label": "Bank Warranty Letter Reservation Commission Advance Payment",
            #     "default": 0
            # },
            # {
            #     "fieldname": "final_bank_warranty_letter_commission",
            #     "fieldtype": "Percent",
            #     "insert_after": "bank_warranty_letter_reservation_commission_advance_payment",
            #     "label": "Final Bank Warranty Letter Commission",
            #     "default": 0
            # },

            # {
            #     "fieldname": "cheques_commissions_column",
            #     "fieldtype": "Column Break",
            #     "insert_after": "final_bank_warranty_letter_commission",
            #     "label": "Cheque",
            # },
            # {
            #     "fieldname": "cheque_commission",
            #     "fieldtype": "Float",
            #     "insert_after": "cheques_commissions_column",
            #     "label": "Cheque Commission",
            #     "default": 0
            # },
            # {
            #     "fieldname": "collect_cheque_commission",
            #     "fieldtype": "Float",
            #     "insert_after": "cheque_commission",
            #     "label": "Collect Cheque Commission",
            #     "default": 0
            # },
            # {
            #     "fieldname": "reject_cheque_commission",
            #     "fieldtype": "Float",
            #     "insert_after": "collect_cheque_commission",
            #     "label": "Reject Cheque Commission",
            #     "default": 0
            # },
            # {
            #     "fieldname": "bank_transfer_commission",
            #     "fieldtype": "Float",
            #     "insert_after": "reject_cheque_commission",
            #     "label": "Bank Transfer Commission",
            #     "default": 0
            # },
            # {
            #     "fieldname": "issue_cheque_commission",
            #     "fieldtype": "Float",
            #     "insert_after": "bank_transfer_commission",
            #     "label": "Issue Cheque Commission",
            #     "default": 0
            # },
            # {
            #     "fieldname": "initial_bank_warranty_letter_commission_reservation",
            #     "fieldtype": "Percent",
            #     "insert_after": "issue_cheque_commission",
            #     "label": "Initial Bank Warranty Letter Commission Reservation",
            #     "default": 0
            # },
            # {
            #     "fieldname": "cheques_section2",
            #     "fieldtype": "Section Break",
            #     "insert_after": "issue_cheque_commission",
            #     "label": "Cheques Section",
            # },
            {
                "fieldname": "bank_commissions",
                "fieldtype": "Table",
                "insert_after": "cheques_commission_section",
                "label": "Bank Commissions",
                "options": "Bank Commissions",
                "reqd": 1
            },
        ],
        "Payment Entry": [
            {
                "fieldname": "drawn_bank",
                "fieldtype": "Link",
                "insert_after": "payment_order_status",
                "label": "Drawn Bank",
                "options": "Bank",
                "read_only": 1
            },
            {
                "fieldname": "cheque_type",
                "fieldtype": "Select",
                "insert_after": "drawn_bank",
                "label": "Cheque Type",
                "options": "\nOpened\nCrossed\nEndorsed",
                "read_only": 1
            },
            {
                "fieldname": "cash_mod_of_payment",
                "fieldtype": "Link",
                "insert_after": "mode_of_payment",
                "label": "Cash Mode Of Payment",
                "options": "Mode of Payment",
                "allow_on_submit": 1,
            },
            {
                "fieldname": "first_benefit",
                "fieldtype": "Data",
                "insert_after": "cheque_type",
                "label": "First Benefit",
                "read_only": 1
            },
            {
                "fieldname": "person_name",
                "fieldtype": "Data",
                "insert_after": "first_benefit",
                "label": "Person Name",
                "read_only": 1
            },
            {
                "fieldname": "cheque",
                "fieldtype": "Link",
                "insert_after": "cash_mod_of_payment",
                "label": "Cheque",
                "options": "Cheque",
                "read_only": 1
            },
            {
                "fieldname": "cheque_status",
                "fieldtype": "Select",
                "insert_after": "cheque",
                "label": "Cheque Status",
                "read_only": 1,
                "options": "\n".join(cheque_status),
                "allow_on_submit": 1,
                "in_list_view": 1,
                "in_filter": 1,
                "in_standard_filter": 1,
            },

            {
                "fieldname": "endorse_cheque",
                "fieldtype": "Check",
                "insert_after": "cheque_status",
                "label": "Endorse Cheque",
                "depends_on": "cheque",
                "read_only_depends_on": "eval:doc.cheque_status!='New'",
                "allow_on_submit": 1
            },
            {
                "fieldname": "endorsed_party_type",
                "fieldtype": "Select",
                "insert_after": "endorse_cheque",
                "label": "Endorsed Party Type",
                "options": "\nSupplier\nCustomer",
                "depends_on": "eval:doc.endorse_cheque",
                "read_only_depends_on": "eval:doc.cheque_status!='New'",
                "mandatory_depends_on": "eval:doc.endorse_cheque&&doc.cheque_status=='New'",
                "allow_on_submit": 1
            },
            {
                "fieldname": "endorsed_party_name",
                "fieldtype": "Dynamic Link",
                "options": "endorsed_party_type",
                "insert_after": "endorsed_party_type",
                "label": "Endorsed Party Name",
                "depends_on": "eval:doc.endorse_cheque",
                "read_only_depends_on": "eval:doc.cheque_status!='New'",
                "mandatory_depends_on": "eval:doc.endorse_cheque&&doc.cheque_status=='New'",
                "allow_on_submit": 1
            },
            {
                "fieldname": "endorsed_party_account",
                "fieldtype": "Link",
                "options": "Account",
                "insert_after": "endorsed_party_name",
                "label": "Endorsed Party Account",
                "depends_on": "eval:doc.endorse_cheque",
                "read_only_depends_on": "eval:doc.cheque_status!='New'",
                "mandatory_depends_on": "eval:doc.endorse_cheque&&doc.cheque_status=='New'",
                "allow_on_submit": 1
            },
            {
                "fieldname": "bank_details_section",
                "fieldtype": "Section Break",
                "insert_after": "paid_to_account_balance",
                "label": "Bank Details",
                "depends_on": "cheque"
            },
            {
                "fieldname": "drawn_bank_account",
                "fieldtype": "Link",
                "insert_after": "bank_details_section",
                "label": "Bank Account",
                "options": "Bank Account",
                "allow_on_submit": 1,
                "depends_on": "cheque"
            },
            {
                "fieldname": "cheques_payable_account",
                "fieldtype": "Link",
                "insert_after": "drawn_bank_account",
                "label": "Cheques Payable Account",
                "options": "Account",
                "read_only": 1,
                "fetch_from": "drawn_bank_account.cheques_payable_account",
                "allow_on_submit": 1,
                "depends_on": "drawn_bank_account"
            },
            {
                "fieldname": "bank_details_column",
                "fieldtype": "Column Break",
                "insert_after": "cheques_payable_account",
                "label": "",
            },

            {
                "fieldname": "drawn_account",
                "fieldtype": "Link",
                "insert_after": "bank_details_column",
                "label": "Bank Company Account",
                "options": "Account",
                "read_only": 1,
                "fetch_from": "drawn_bank_account.account",
                "allow_on_submit": 1,
                "depends_on": "drawn_bank_account"
            },
            {
                "fieldname": "cheques_receivable_account",
                "fieldtype": "Link",
                "insert_after": "drawn_account",
                "label": "Cheques Receivable Account",
                "options": "Account",
                "read_only": 1,
                "fetch_from": "drawn_bank_account.cheques_receivable_account",
                "allow_on_submit": 1,
                "depends_on": "drawn_bank_account"
            },
            # {
            #     "fieldname": "bank_details_column",
            #     "fieldtype": "Column Break",
            #     "insert_after": "cheques_receivable_account",
            #     "label": "",
            # },
            # {
            #     "fieldname": "collect_cheque_commission",
            #     "fieldtype": "Float",
            #     "insert_after": "bank_details_column",
            #     "label": "Collect Cheque Commission",
            #     "default": 0,
            #     "read_only": 1,
            #     "fetch_from": "drawn_bank_account.collect_cheque_commission",
            #     "allow_on_submit": 1,
            #     "depends_on": "drawn_bank_account"
            # },
            # {
            #     "fieldname": "issue_cheque_commission",
            #     "fieldtype": "Float",
            #     "insert_after": "collect_cheque_commission",
            #     "label": "Issue Cheque Commission",
            #     "default": 0,
            #     "read_only": 1,
            #     "fetch_from": "drawn_bank_account.issue_cheque_commission",
            #     "allow_on_submit": 1,
            #     "depends_on": "drawn_bank_account"
            # },
            # {
            #     "fieldname": "reject_cheque_commission",
            #     "fieldtype": "Float",
            #     "insert_after": "issue_cheque_commission",
            #     "label": "Reject Cheque Commission",
            #     "default": 0,
            #     "read_only": 1,
            #     "fetch_from": "drawn_bank_account.reject_cheque_commission",
            #     "allow_on_submit": 1,
            #     "depends_on": "drawn_bank_account"
            # },
            # {
            #     "fieldname": "bank_transfer_commission",
            #     "fieldtype": "Percent",
            #     "insert_after": "reject_cheque_commission",
            #     "label": "Bank Transfer Commission",
            #     "default": 0,
            #     "read_only": 1,
            #     "fetch_from": "drawn_bank_account.bank_transfer_commission",
            #     "allow_on_submit": 1,
            #     "depends_on": "drawn_bank_account"
            # },
            {
                "fieldname": "section_tracks",
                "fieldtype": "Section Break",
                "insert_after": "payment_order",
                "label": "Section Tracks",
            },
            {
                "fieldname": "cheque_tracks",
                "fieldtype": "Table",
                "options":"Cheque Tracks",
                "insert_after": "section_tracks",
                "label": "Cheque Tracks",
                "read_only": 1,
                "allow_on_submit": 1,
            },


        ],
        "Journal Entry": [
            {
                "fieldname": "payment_entry",
                "fieldtype": "Link",
                "insert_after": "column_break1",
                "label": "Payment Entry",
                "options": "Payment Entry",
                "read_only": 1,
                "allow_on_submit": 1
            },
            {

                "fieldname": "cheque",
                "fieldtype": "Link",
                "insert_after": "payment_entry",
                "label": "Cheque",
                "options": "Cheque",
                "read_only": 1,
                "allow_on_submit": 1,
                "fetch_from": "payment_entry.cheque"
            },
            {
                "fieldname": "cheque_status",
                "fieldtype": "Data",
                "insert_after": "cheque",
                "label": "Cheque Status",
                "read_only": 1,
                "allow_on_submit": 1,
            },

        ]
    },
    "properties": [{
        # "doctype":"Journal Entry Account",
        # "doctype_or_field":"DocField",
        # "fieldname":"reference_type",
        # "property":"options",
        # "property_type":"Text",
        # "value": "\nSales Invoice\nPurchase Invoice\nJournal Entry\nSales Order\nPurchase Order\nExpense Claim\nAsset\nLoan\nPayroll Entry\nEmployee Advance\nExchange Rate Revaluation\nInvoice Discounting\nFees\nComparison\nClearance\nTender\nPayroll Month\nCheque\nPay Document\nReceipt Document\nPayment Entry"
    }],
    'on_setup': 'dynamic.cheques.setup.install'
}
