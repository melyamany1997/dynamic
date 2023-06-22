// Copyright (c) 2021, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on("Pay and Receipt Document", {
  refresh: function (frm) {
    if (frm.doc.docstatus > 0) {
      frm.add_custom_button(
        __("Ledger"),
        function () {
          frappe.route_options = {
            voucher_no: frm.doc.journal_entry,
            from_date: frm.doc.posting_date,
            to_date: moment(frm.doc.modified).format("YYYY-MM-DD"),
            company: frm.doc.company,
            show_cancelled_entries: frm.doc.docstatus === 2,
          };
          frappe.set_route("query-report", "General Ledger");
        },
        __("View")
      );
    }
    frm.events.set_base_amount(frm);
    frm.set_query("account", function (doc) {
      return {
        filters: {
          is_group: 0,
          account_type: doc.mode_of_payment,
          company: doc.company,
        },
      };
    });

    frm.set_query("against_account", function (doc) {
      return {
        filters: {
          is_group: 0,
          // "account_type": doc.mode_of_payment ,
          company: doc.company,
        },
      };
    });
    frm.set_query("account", "accounts", function (doc) {
      return {
        filters: {
          is_group: 0,
          // "account_type": doc.mode_of_payment ,
          company: doc.company,
        },
      };
    });
    frm.set_query("party_type", "accounts", function () {
      return {
        query: "erpnext.setup.doctype.party_type.party_type.get_party_type",
      };
    });
  },
  set_totals: function (frm) {
    frappe.call({
      method: "set_totals",
      doc: frm.doc,
      callback: function (r) {
        frm.refresh_field("total");
        frm.refresh_field("difference");
        frm.refresh_field("accounts");
      },
    });
  },
  currency(frm) {
    if (frm.doc.currency) {
      frappe.call({
        method: "get_conversion_rate",
        doc: frm.doc,
        callback: function (r) {
          frm.events.set_base_amount(frm);
          frm.refresh_field("exchange_rate");
          frm.events.set_totals(frm);
        },
      });
    }
  },
  amount(frm) {
    frm.events.set_base_amount(frm);
    frm.events.set_totals(frm);
  },
  exchange_rate(frm) {
    frm.events.set_base_amount(frm);
    frm.events.set_totals(frm);
  },
  set_base_amount(frm) {
    frm.doc.base_amount = 0;
    if (frm.doc.amount && frm.doc.exchange_rate) {
      frm.doc.base_amount = frm.doc.amount * frm.doc.exchange_rate;
    }
    frm.refresh_field("base_amount");
  },
});

frappe.ui.form.on("Pay and Receipt Account", {
  accounts_add: function (frm, cdt, cdn) {
    frm.events.set_totals(frm);
  },
  amount: function (frm, cdt, cdn) {
    frm.events.set_totals(frm);
  },
});
