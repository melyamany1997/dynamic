
import copy
import frappe
from frappe.utils import get_site_url
from frappe.utils.data import get_host_name_from_request, get_url, url_contains_port
from frappe.utils.jinja import render_template
from frappe.utils.pdf import get_pdf


@frappe.whitelist(allow_guest=True)
def download_pdf(name, doctype="Sales Invoice", format="Invoice Tax", doc=None, no_letterhead=0):
    doc = frappe.get_doc("Sales Invoice", name)
    html = render_template(
        "dynamic_accounts/print_format/invoice_tax/invoice_tax.html", {"doc": doc}, is_path=1)
    frappe.local.response.filename = "{name}.pdf".format(
        name=name.replace(" ", "-").replace("/", "-"))
    frappe.local.response.filecontent = get_pdf(html)
    frappe.local.response.type = "pdf"


@frappe.whitelist(allow_guest=True)
def get_invoice_tax_data(doc):
    doc = frappe.get_doc("Sales Invoice", doc)
    total_discount_amount = sum([(x.discount_amount or 0) for x in doc.items])
    total_tax_amount = sum([(x.tax_amount or 0) for x in doc.items])
    # server_url = frappe.local.conf.host_name or frappe.local.conf.hostname
    server_url = get_url(full_address=True)
    port = frappe.conf.nginx_port or frappe.conf.http_port or frappe.conf.webserver_port
    if not url_contains_port(server_url) and port and str(port) != "80":
        server_url = server_url + ':' + str(port)

    return {
        "total_discount_amount": total_discount_amount,
        "total_tax_amount": total_tax_amount,
        "server_url": server_url,
    }


@frappe.whitelist(allow_guest=True)
def get_components_summary(doc, component_type='earning'):
	doc = frappe.get_doc("Salary Slip", doc)
	totals = {}
	result = []
	for row in getattr(doc, component_type, []):
		totals.setdefault(row.salary_component, 0)
		totals[row.salary_component] += (row.amount or 0)

	for k, v in totals.items():
		result.append(frappe._dict({
			'salary_component': k,
			'amount': v
		}))

	return result
