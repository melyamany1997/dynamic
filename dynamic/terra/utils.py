from erpnext.accounts.utils import update_reference_in_journal_entry, update_reference_in_payment_entry, validate_allocated_amount
import frappe 
import erpnext 
from frappe import _, throw

from frappe.utils import cstr, flt, get_link_to_form


def reconcile_against_document(args):
	"""
	Cancel PE or JV, Update against document, split if required and resubmit
	"""
	# To optimize making GL Entry for PE or JV with multiple references
	reconciled_entries = {}
	for row in args:
		if not reconciled_entries.get((row.voucher_type, row.voucher_no)):
			reconciled_entries[(row.voucher_type, row.voucher_no)] = []

		reconciled_entries[(row.voucher_type, row.voucher_no)].append(row)

	for key, entries in reconciled_entries.items():
		voucher_type = key[0]
		voucher_no = key[1]

		# cancel advance entry
		doc = frappe.get_doc(voucher_type, voucher_no)
		frappe.flags.ignore_party_validation = True
		doc.make_gl_entries(cancel=1, adv_adj=1)

		for entry in entries:
			check_if_advance_entry_modified(entry)
			validate_allocated_amount(entry)

			# update ref in advance entry
			if voucher_type == "Journal Entry":
				update_reference_in_journal_entry(entry, doc, do_not_save=True)
			else:
				update_reference_in_payment_entry(entry, doc, do_not_save=True)

		doc.save(ignore_permissions=True)
		# re-submit advance entry
		doc = frappe.get_doc(entry.voucher_type, entry.voucher_no)
		doc.make_gl_entries(cancel=0, adv_adj=1)
		frappe.flags.ignore_party_validation = False

		if entry.voucher_type in ("Payment Entry", "Journal Entry"):
			doc.update_expense_claim()


def check_if_advance_entry_modified(args):
    """
    check if there is already a voucher reference
    check if amount is same
    check if jv is submitted
    """
    if not args.get("unreconciled_amount"):
        args.update({"unreconciled_amount": args.get("unadjusted_amount")})

    ret = None
    if args.voucher_type == "Journal Entry":
        ret = frappe.db.sql(
            """
            select t2.{dr_or_cr} from `tabJournal Entry` t1, `tabJournal Entry Account` t2
            where t1.name = t2.parent and t2.account = %(account)s
            and t2.party_type = %(party_type)s and t2.party = %(party)s
            and (t2.reference_type is null or t2.reference_type in ("", "Quotation", "Sales Order", "Purchase Order"))
            and t1.name = %(voucher_no)s and t2.name = %(voucher_detail_no)s
            and t1.docstatus=1 """.format(
                dr_or_cr=args.get("dr_or_cr")
            ),
            args,
        )
    else:
        party_account_field = (
            "paid_from" if erpnext.get_party_account_type(args.party_type) == "Receivable" else "paid_to"
        )
        sql = """select t1.name
                from `tabPayment Entry` t1, `tabPayment Entry Reference` t2
                where
                    t1.name = t2.parent and t1.docstatus = 1
                    and t1.name = '%(voucher_no)s' and t2.name = '%(voucher_detail_no)s'
                    and t1.party_type = '%(party_type)s' and t1.party = '%(party)s' and t1.{0} = '%(account)s'
                    and t2.reference_doctype in ("", "Quotation", "Sales Order", "Purchase Order")
                    and t2.allocated_amount = '%(unreconciled_amount)s'
            """.format(
                    party_account_field
                )%args
        # frappe.throw(sql)
        if args.voucher_detail_no:
            ret = frappe.db.sql(
                """select t1.name
                from `tabPayment Entry` t1, `tabPayment Entry Reference` t2
                where
                    t1.name = t2.parent and t1.docstatus = 1
                    and t1.name = %(voucher_no)s and t2.name = %(voucher_detail_no)s
                    and t1.party_type = %(party_type)s and t1.party = %(party)s and t1.{0} = %(account)s
                    and t2.reference_doctype in ("", "Quotation", "Sales Order", "Purchase Order")
                    and t2.allocated_amount = %(unreconciled_amount)s
            """.format(
                    party_account_field
                ),
                args,
            )
        else:
            ret = frappe.db.sql(
                """select name from `tabPayment Entry`
                where
                    name = %(voucher_no)s and docstatus = 1
                    and party_type = %(party_type)s and party = %(party)s and {0} = %(account)s
                    and unallocated_amount = %(unreconciled_amount)s
            """.format(
                    party_account_field
                ),
                args,
            )

    if not ret:
        throw(_("""Payment Entry has been modified after you pulled it. Please pull it again."""))


def update_reimbursed_amount(doc, amount):

	doc.total_amount_reimbursed += amount
	frappe.db.set_value(
		"Expense Claim", doc.name, "total_amount_reimbursed", doc.total_amount_reimbursed
	)

	doc.set_status()
	frappe.db.set_value("Expense Claim", doc.name, "status", doc.status)


def get_outstanding_amount_for_claim(claim):
	if isinstance(claim, str):
		claim = frappe.db.get_value(
			"Expense Claim",
			claim,
			(
				"total_sanctioned_amount",
				"total_taxes_and_charges",
				"total_amount_reimbursed",
				"total_advance_amount",
			),
			as_dict=True,
		)

	outstanding_amt = (
		flt(claim.total_sanctioned_amount)
		+ flt(claim.total_taxes_and_charges)
		- flt(claim.total_amount_reimbursed)
		- flt(claim.total_advance_amount)
	)

	return outstanding_amt