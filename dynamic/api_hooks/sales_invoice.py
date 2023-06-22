import frappe
from frappe import _
from datetime import datetime ,date
from functools import reduce
from html2text import re
from collections import Counter
from operator import add
DOMAINS = frappe.get_active_domains()

"""  
Fiscal Year Is The Committion Function Main Key 
Under The  Fiscal Year Sales Invocie Month will Be The Count Method 

"""


#caculate total item group sales amount ant qty 
def count_total_item_group_qty_amount(invoice):
    group_qty = [{item.get("item_group"): item.get("qty")} for item in invoice.items ]
    group_amount = [{item.get("item_group"): item.get("amount")} for item in invoice.items ]
    #get Sum qty amd amount for each item group 
    sum_group_qty  = reduce(add, (map(Counter, group_qty )))
    sum_group_amount  = reduce(add, (map(Counter, group_amount )))
 
    for person in invoice.sales_team :
        sales_person = validate_sales_person(person.sales_person)
        person_percent  = float(person.allocated_percentage) /100 
        #maping item Group with commision template -- >
        if not sales_person :
            
            return 0 
            
        target_ietm_group =[]
        for target in sales_person.targets :
            tem_name= frappe.db.sql(""" SELECT name FROM 
                        `tabCommission Template` WHERE name = '{target.commission_template}'
                         """,as_dict =1)

   
            if tem_name and len(tem_name) > 0  :
                template = frappe.get_doc("Commission Template", ) 
           
            child_list =  {target.item_group : target.commission_template } if (target.commission_template and target.item_group
            )  in [k for k,v in sum_group_qty.items() ] else None
              
            if child_list :
                target_ietm_group.append(child_list)
        for commetion in  target_ietm_group :
            #craete Commetion log
            #check invocie old commetions 
            for k,v in commetion.items() :
                item_group = k
            old_log = frappe.db.sql(f""" SELECT name FROM `tabSales Person Commetion` WHERE 
            sales_person = '{person.sales_person}' and invocie='{invoice.name}' and 
            item__group = '{item_group}' 
                """,as_dict =1)
            if old_log and len(old_log) > 0 :
                log = frappe.get_doc("Sales Person Commetion" ,old_log[0].get('name') )
            else: 
                log = frappe.new_doc("Sales Person Commetion" )
            log.sales_person = person.sales_person
            log.invocie = invoice.name
            for k,v in commetion.items() :
               log.item__group = k 
               log.commission_template = v
            for e ,d in sum_group_qty.items():
                if e ==log.item__group :
                    log.invoice_qty = d
            for e ,d in sum_group_amount.items():
                if e ==log.item__group :
                    log.invocie_amount = d
            log.save(ignore_permissions=True)
    #frappe.throw(str(sum_group_amount)) 
def validate_fiscal_year(year):
    """   this function Check if the year is Disabled  and If company Belong to The year  """

    fiscal_year = frappe.get_doc("Fiscal Year" , year)
    if fiscal_year.disabled :
        frappe.throw("You Can Not Caculate Commetion To  Disabled Year   ")
        return 0
    
    company =frappe.defaults.get_user_default("Company")
    if fiscal_year.companies :
        company_list = [co.company for co in fiscal_year.companies ]
        if  company not in company_list :
            frappe.throw(f""" Commetion  Table dos Not Belong To Company {company}""")
            return 0
        
    return True



def validate_sales_person(name) :
    """  Get All Sales Person From The Invoice """
   
    sales_person = frappe.get_doc("Sales Person" , name)
    if sales_person.is_group == 1 :
        pass
        return 0 
    if sales_person.enabled == 0 :
        frappe.throw(f""" Sales Person {name} Is Not Active \n
         Please Enable Sales Person Before Complete Sales Invocie """)
    """Get Person Template  """
    if not sales_person.targets :
        return 0
    
    for target in sales_person.targets :
        #1 - validate Fiscal Year 
        fiscal_year = target.fiscal_year
        if not fiscal_year :
            frappe.throw(""" Please Set fiscal year To Sales Person Target Table """)
        validate_fiscal_year(fiscal_year)
        #validate Target  amount , Qty And get Mothly Target 
        # vaildate targey qty
        if not  target.commission_template  :
            return sales_person
        template = frappe.get_doc("Commission Template" ,target.commission_template )
        if target.target_qty > 0  and target.target_amount > 0 :
            frappe.throw(""" Please Set arget Qty  or  Target Amount to 0 value in Target Table """)
        if target.target_qty == 0  and target.target_amount == 0 :
            frappe.throw(""" Please Set arget Qty  or  Target Amount to  value in Target Table """)
        #validate template with target qty 
        if target.target_qty > 0  and target.commission_template:
            if template.base_on == "Amount" :
                      frappe.throw(""" Commission Base On Qty Please Select   Commission Template Based On Qty """)
           
        if target.target_amount > 0  and target.commission_template:
            if template.base_on == "Qty" :
                      frappe.throw(""" Commission Base On Qty Please Select   Commission Template Based On Qty """)
        #caclulate Mothly Invoice For sales Man 
       
        #test Area Not Used
        caculation_sql =    f""" SELECT `tabSales Invoice`.posting_date as date , 
                                `tabSales Invoice Item`.amount as amount
                                FROM 
                                `tabSales Invoice` INNER JOIN 
                                `tabSales Invoice Item`
                                ON `tabSales Invoice`.name = `tabSales Invoice Item`.parent
                                WHERE `tabSales Invoice`.name in 
                                (SELECT parent FROM `tabSales Team` WHERE sales_person = '{name}')
                                AND `tabSales Invoice`.docstatus = 1
                            """
        # data = frappe.db.sql(caculation_sql ,as_dict=1)
        # frappe.throw(str(data))
        return sales_person
"""  this method Will Run only if Moyate in Active Domain """
def filetr_item_base_on_template(items , person , pdate ,case) :
    #caculate item percent 
    # frappe.throw(str(items))
    date_list = str(pdate).split('-')
    year_name = date_list[0]
    month_name = date_list[1]
    item_group_amount = []
    sales_person = frappe.get_doc("Sales Person" ,person)
    commetion_item_group = [target.item_group for target in sales_person.targets]
    # for target in sales_person.targets :
    #     if target.
    invocie_item_groups = [item.get("item_group") for item in items ]
    for group in invocie_item_groups :
        if group not in invocie_item_groups :
            invocie_item_groups.pop(group)
    # frappe.throw("str" +str(invocie_item_groups) + "Str" +str(commetion_item_group) ) 

    """  
    Caculate Item Group total Sales For Sales Person 

    """
    #remove Duplicated FROM  invocie_item_groups
    invocie_item_groups = set(invocie_item_groups)
    item_group_tuple = list(invocie_item_groups)
    total_grant = 0
    for item_group in item_group_tuple :
        local_sales = 0
        local_qty = 0 
        for item in items :
            if item.get("item_group") == item_group :
                local_sales = local_sales + float(item.get("amount"))
                local_qty = local_qty + float(item.get("qty"))
        start_date = f"""{year_name}-{month_name}-01"""
        end_date = f"""{year_name}-{month_name}-31"""
        caculation_sql =    f"""    SELECT 
                                    SUM(`tabSales Invoice Item`.amount) as amount ,
                                    SUM(`tabSales Invoice Item`.qty) as qty
                                    FROM 
                                    `tabSales Invoice` INNER JOIN 
                                    `tabSales Invoice Item`
                                    ON `tabSales Invoice`.name = `tabSales Invoice Item`.parent
                                    WHERE `tabSales Invoice`.name in 
                                    (SELECT parent FROM `tabSales Team` WHERE sales_person = '{person}')
                                    AND `tabSales Invoice`.docstatus = 1 and
                                    `tabSales Invoice Item`.item_group = '{item_group}' and 
                                    `tabSales Invoice`.posting_date between '{start_date }' and '{end_date}' 
                                """
       
        old_sales_amount = 0 
        old_sales_qty = 0
        # frappe.throw(str(local_qty))
        sum_amount = frappe.db.sql(caculation_sql ,as_dict=1)
        if sum_amount and len(sum_amount) > 0 :
            old_sales_amount = sum_amount[0].get("amount")   
            old_sales_qty =    sum_amount[0].get("qty")
        total_monthly_sales = float(old_sales_amount or 0) +float(local_sales or 0)
        total_monthly_qty = float(old_sales_qty or 0 ) + float(local_qty or 0)
        # find Commission in Commission Template
        # frappe.throw(str(total_monthly_qty))
        template_sql = f""" SELECT commission_template FROM `tabTarget Detail`  WHERE    
        fiscal_year = '{year_name}' and parent = '{person}' and item_group = '{item_group}'

            """
        commition_amount = 0
        commition_rate = 0 
        grant_commition = 0 
        template = frappe.db.sql(template_sql ,as_dict =1)
        if template and len(template) > 0 and template[0].get("commission_template") :
            local_template = frappe.get_doc("Commission Template" , template[0].get("commission_template"))
            if local_template.base_on ==  "Amount" :
                for in_amount in local_template.templat  :
                    if float(total_monthly_sales) > float(in_amount.amount_from or  0)  and local_template.base_on ==  "Amount":
                        commition_amount  = float(in_amount.commission_amount or 0 )
                        commition_rate    = float(in_amount.commission_rate or 0 )
            if local_template.base_on ==  "Qty" : 
                for in_amount in local_template.templat  :
                    if float(total_monthly_qty) > float(in_amount.amount_from or  0) :
                        commition_amount  = float(in_amount.commission_amount or 0 ) * total_monthly_qty
                        commition_rate    = float(in_amount.commission_rate or 0 )* total_monthly_qty
                        
        grant_commition = commition_amount
        if  commition_rate  > 0 :
            grant_commition = float(total_monthly_sales) * (float(commition_rate or 0 ) /100)
        if case == "submit" :
            """ UPDATE old value  """
            sql_chil_str = ''
            parent_invoice = frappe.db.sql(f""" SELECT name FROM `tabSales Invoice` WHERE name in 
                   (SELECT parent FROM `tabSales Team` WHERE sales_person = '{person}')
                   and  posting_date between '{start_date }' and '{end_date}'""" ,as_dict=1)
            for i in parent_invoice :
                 sql_chil_str =  sql_chil_str + "'" + str(i.get("name")) + "'"+ ','
            update_sql = frappe.db.sql(f""" UPDATE  `tabSales Team` SET incentives  = 0
                         WHERE sales_person = '{person}'  and parent in ({sql_chil_str[:-1] })""")
            
            # frappe.throw(str(update_sql))
            frappe.db.commit()
        total_grant = total_grant + grant_commition
        
    return total_grant 
# @frappe.whitelist()
def   validate_sales_invocie_to_moyate(self):
    """  
    Calculate the Commetion For Sales Person Base on Commission Template
    Disabled Sales Person throw Error
    if Sales Person is Group function will not work with no Errors   
    How To Use  : - 
                1 - Create Commission Table in Commission Table List
                2 - In Sales Person Add The Link of The Commition table To the Targets Table 
                3 - 
    """
    count_total_item_group_qty_amount(self)
    if self.sales_team :
        # frappe.throw(" Sales Team Found")
        case =  "submit" if self._action == "submit" else "draft"
        for person in self.sales_team :
            sales_person = validate_sales_person(person.sales_person)
            #caculate Commition Base On total Amount Before Tax 
            cal_precent = float(person.allocated_percentage) /100
            #data = allocated_percentage ,  sales_person , Items ,  date
            filtersitems = filetr_item_base_on_template([{  "item_code"  :item.item_code ,
                                                            "item_group" :item.item_group ,
                                                            "amount"     :float(item.base_amount) *cal_precent  ,
                                                            "qty" :item.qty} 
                                                             for item in  self.items] , 
                                                             person.sales_person ,
                                                             self.posting_date ,
                                                             case )
            person.incentives = filtersitems
    


