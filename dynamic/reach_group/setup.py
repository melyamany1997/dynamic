


import frappe




def setup_reach():
    tr1=frappe.new_doc('Translation')
    tr1.language = 'en-US'
    tr1.source_text = 'Cash'
    tr1.translated_text = 'كاش'
    tr1.save()

    tr2=frappe.new_doc('Translation')
    tr2.language = 'en-US'
    tr2.source_text = 'Payments'
    tr2.translated_text = 'دفعات'
    tr2.save()


    tr4=frappe.new_doc('Translation')
    tr4.language = 'ar'
    tr4.source_text = 'PrePaid'
    tr4.translated_text = 'أجل'
    tr4.save()

    tr5=frappe.new_doc('Translation')
    tr5.language = 'en-US'
    tr5.source_text = 'PAN'
    tr5.translated_text = 'Address'
    tr5.save()

    tr6=frappe.new_doc('Translation')
    tr6.language = 'ar'
    tr6.source_text = 'PAN'
    tr6.translated_text = 'عنوان العميل'
    tr6.save()
    # frappe.msgprint('setup done')


    pass