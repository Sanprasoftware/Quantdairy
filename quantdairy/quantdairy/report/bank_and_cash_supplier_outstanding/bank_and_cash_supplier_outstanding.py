# import frappe
# from frappe.utils import flt
# from erpnext.accounts.report.customer_ledger_summary.customer_ledger_summary import (
#     PartyLedgerSummaryReport,
# )

# def execute(filters=None):
#     args = {
# 		"party_type": "Supplier",
# 		"naming_by": ["Buying Settings", "supp_master_name"],
# 	}
#     report = PartyLedgerSummaryReport(filters)
#     columns, data = report.run(args)
    
#     # Remove unwanted columns
#     # labels_to_remove = ["Paid Amount", "Debit Note"]
#     # columns = [column for column in columns if column["label"] not in labels_to_remove]

#     # Add new columns
#     new_columns = [
#         {'label': 'Cash Receipts', 'fieldname': 'cash_amount', 'fieldtype': 'Currency', 'options': 'currency', 'width': 120},
#         {'label': 'Bank Receipts', 'fieldname': 'bank_amount', 'fieldtype': 'Currency', 'options': 'currency', 'width': 120}
#     ]
#     columns.extend(new_columns)
    
#     from_date = filters.get('from_date')
#     to_date = filters.get('to_date')
#     data = add_receipts_data(data, from_date, to_date)

#     return columns, data

# def add_receipts_data(data, from_date, to_date):
#     bank_receipts = {}
#     cash_receipts = {}

#     bank_entries = frappe.db.sql("""
#         SELECT party, SUM(paid_amount) AS total_paid
#         FROM `tabPayment Entry`
#         WHERE posting_date BETWEEN %s AND %s
#         AND payment_type = 'Pay'
#         AND mod_type = 'Bank' AND docstatus = 1 
#         GROUP BY party
#     """, (from_date, to_date), as_dict=True)

#     cash_entries = frappe.db.sql("""
#         SELECT party, SUM(paid_amount) AS total_paid
#         FROM `tabPayment Entry`
#         WHERE posting_date BETWEEN %s AND %s
#         AND payment_type = 'Pay'
#         AND mod_type = 'Cash' AND docstatus = 1 
#         GROUP BY party
#     """, (from_date, to_date), as_dict=True)

#     for entry in bank_entries:
#         bank_receipts[entry['party']] = flt(entry['total_paid'])

#     for entry in cash_entries:
#         cash_receipts[entry['party']] = flt(entry['total_paid'])

#     for row in data:
#         party = row.get('party')
#         row['cash_amount'] = cash_receipts.get(party, 0.0)
#         row['bank_amount'] = bank_receipts.get(party, 0.0)

#     return data
import frappe
from frappe.utils import flt
from quantdairy.quantdairy.report.customer_ledger_summary_report.customer_ledger_summary_report import (
    PartyLedgerSummaryReport,
)

def execute(filters=None):
    args = {
        "party_type": "Supplier",
        "naming_by": ["Buying Settings", "supp_master_name"],
    }
    
    # Ensure filters is not None
    filters = filters or {}
    
    # Extract mode_of_payment filter (list of selected modes)
    mode_of_payment_filter = filters.get('mode_of_payment') or []

    report = PartyLedgerSummaryReport(filters)
    columns, data = report.run(args)
    
    # Add new columns
    new_columns = [
        {'label': 'Cash Receipts', 'fieldname': 'cash_amount', 'fieldtype': 'Currency', 'options': 'currency', 'width': 120},
        {'label': 'Bank Receipts', 'fieldname': 'bank_amount', 'fieldtype': 'Currency', 'options': 'currency', 'width': 120}
    ]
    columns.extend(new_columns)
    
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    data = add_receipts_data(data, from_date, to_date, mode_of_payment_filter)

    return columns, data

def add_receipts_data(data, from_date, to_date, mode_of_payment_filter):
    bank_receipts = {}
    cash_receipts = {}

    # Prepare the SQL query with mode_of_payment filter
    mode_of_payment_conditions = ''
    if mode_of_payment_filter:
        placeholders = ', '.join(['%s'] * len(mode_of_payment_filter))
        mode_of_payment_conditions = f"AND mode_of_payment IN ({placeholders})"

    bank_entries = frappe.db.sql(f"""
        SELECT party, SUM(paid_amount) AS total_paid
        FROM `tabPayment Entry`
        WHERE posting_date BETWEEN %s AND %s
        AND payment_type = 'Pay'
        AND mod_type = 'Bank' AND docstatus = 1 
        {mode_of_payment_conditions}
        GROUP BY party
    """, (from_date, to_date) + tuple(mode_of_payment_filter), as_dict=True)

    cash_entries = frappe.db.sql(f"""
        SELECT party, SUM(paid_amount) AS total_paid
        FROM `tabPayment Entry`
        WHERE posting_date BETWEEN %s AND %s
        AND payment_type = 'Pay'
        AND mod_type = 'Cash' AND docstatus = 1 
        {mode_of_payment_conditions}
        GROUP BY party
    """, (from_date, to_date) + tuple(mode_of_payment_filter), as_dict=True)

    for entry in bank_entries:
        bank_receipts[entry['party']] = flt(entry['total_paid'])

    for entry in cash_entries:
        cash_receipts[entry['party']] = flt(entry['total_paid'])

    for row in data:
        party = row.get('party')
        row['cash_amount'] = cash_receipts.get(party, 0.0)
        row['bank_amount'] = bank_receipts.get(party, 0.0)

    return data
