# Copyright (c) 2024, quantdairy and contributors
# For license information, please see license.txt
import frappe 
from frappe import _
from erpnext.accounts.report.customer_ledger_summary.customer_ledger_summary import PartyLedgerSummaryReport as BasePartyLedgerSummaryReport

class CustomPartyLedgerSummaryReport(BasePartyLedgerSummaryReport):
    def get_additional_columns(self):
        columns = super().get_additional_columns() or []
        
        if self.filters.party_type == "Supplier":
            custom_columns = [
                {
                    "label": _("Purchase Invoice"),
                    "fieldname": "purchaseinvoice",
                    "fieldtype": "Link",
                    "options": "Purchase Invoice",
                },
                {
                    "label": _("Bank"),
                    "fieldname": "bank",
                    "fieldtype": "Currency",
                },
                {
                    "label": _("Cash"),
                    "fieldname": "cash",
                    "fieldtype": "Currency",
                },
                {
                    "label": _("Purchase Invoice Total Quantity"),
                    "fieldname": "total_qty",
                    "fieldtype": "Float",
                }
            ]
            # Append custom columns to the columns from the base report
            columns.extend(custom_columns)
            frappe.msgprint(str(columns))
        return columns

    def get_sql(self, filters):
        custom_sql = """
            SELECT 
                pi.name as purchaseinvoice,
                pe.party as supplier, 
                pe.party_name as supplier_name,
                SUM(CASE WHEN pe.mod_type = "Bank" THEN pe.paid_amount ELSE 0 END) AS bank,
                SUM(CASE WHEN pe.mod_type = "Cash" THEN pe.paid_amount ELSE 0 END) AS cash,
                SUM(pi.total_qty) AS total_qty
            FROM 
                `tabPayment Entry` pe
            LEFT JOIN 
                `tabPayment Entry Reference` per ON pe.name = per.parent 
            LEFT JOIN
                `tabPurchase Invoice` pi ON pe.party = pi.supplier
            WHERE
                pe.party = %(party)s AND
                pe.payment_type = "Pay" AND
                pe.party_type = "Supplier" AND
                pe.docstatus = 1 
            GROUP BY 
                pe.party, pe.party_name, pi.name
        """
        return custom_sql

    # Define your custom method
    def custom_method(self, args):
        # Your custom logic here
        pass

def execute(filters=None):
    args = {
        "party_type": "Supplier",
        "naming_by": ["Buying Settings", "supp_master_name"],
    }
    custom_report = CustomPartyLedgerSummaryReport(filters)
    # Call your custom method
    custom_report.custom_method(args)
    return custom_report.run(args)


