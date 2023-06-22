// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Absent Rules', {
	 refresh: function(frm) {

	 },
    sort_table : function (frm, cdt, cdn){

	     var list = ['First Day','Second Day','Third Day','Fourth Day','Fifth Day'] ;
	     var i = 0 ;
	     frm.doc.ruletemplate.forEach((e)=>{
	         e.rule = list [i++];
	         if (! e.deduction)
	             e.deduction = 0
              if (! e.penality)
	             e.penality = 0


	         if (i >=list.length)
             {
                  frm.get_field('ruletemplate').grid.cannot_add_rows = true;
                  refresh_field("ruletemplate");
                  return;
             }
         });
        if (i >= list.length)
        {
              frm.get_field('ruletemplate').grid.cannot_add_rows = true;
        }
        else {
             frm.get_field('ruletemplate').grid.cannot_add_rows = false;
        }
        refresh_field("ruletemplate");
        }
});

frappe.ui.form.on('absent rule templates', {
        rule: function (frm, cdt, cdn) {
            frm.events.sort_table(frm, cdt, cdn);
        },

        ruletemplate_add: function (frm, cdt, cdn) {
             frm.events.sort_table(frm, cdt, cdn);
        },
        ruletemplate_remove: function (frm, cdt, cdn) {
             frm.events.sort_table(frm, cdt, cdn);
        }

});