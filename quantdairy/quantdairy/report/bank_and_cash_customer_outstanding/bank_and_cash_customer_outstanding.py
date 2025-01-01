import frappe
from frappe import _, qb, scrub
from frappe.utils import getdate, nowdate, flt


class PartyLedgerSummaryReport:
    def __init__(self, filters=None):
        self.filters = frappe._dict(filters or {})
        self.filters.from_date = getdate(self.filters.from_date or nowdate())
        self.filters.to_date = getdate(self.filters.to_date or nowdate())

        if not self.filters.get("company"):
            self.filters["company"] = frappe.db.get_single_value("Global Defaults", "default_company")

    def run(self, args):
        if self.filters.from_date > self.filters.to_date:
            frappe.throw(_("From Date must be before To Date"))

        self.filters.party_type = args.get("party_type")
        self.party_naming_by = frappe.db.get_value(args.get("naming_by")[0], None, args.get("naming_by")[1])

        self.get_gl_entries()
        self.get_additional_columns()
        self.get_return_invoices()
        self.get_party_adjustment_amounts()

        columns = self.get_columns()
        data = self.get_data()
        return columns, data

    def get_additional_columns(self):
        """
        Additional Columns for 'User Permission' based access control
        """

        if self.filters.party_type == "Customer":
            self.territories = frappe._dict({})
            self.customer_group = frappe._dict({})

            customer = qb.DocType("Customer")
            result = (
                frappe.qb.from_(customer)
                .select(
                    customer.name, customer.territory, customer.customer_group, customer.default_sales_partner
                )
                .where(customer.disabled == 0)
                .run(as_dict=True)
            )

            for x in result:
                self.territories[x.name] = x.territory
                self.customer_group[x.name] = x.customer_group
        else:
            self.supplier_group = frappe._dict({})
            supplier = qb.DocType("Supplier")
            result = (
                frappe.qb.from_(supplier)
                .select(supplier.name, supplier.supplier_group)
                .where(supplier.disabled == 0)
                .run(as_dict=True)
            )

            for x in result:
                self.supplier_group[x.name] = x.supplier_group

    def get_columns(self):
        columns = [
            {
                "label": _(self.filters.party_type),
                "fieldtype": "Link",
                "fieldname": "party",
                "options": self.filters.party_type,
                "width": 200,
            }
        ]

        if self.party_naming_by == "Naming Series":
            columns.append(
                {
                    "label": _(self.filters.party_type + "Name"),
                    "fieldtype": "Data",
                    "fieldname": "party_name",
                    "width": 110,
                }
            )

        credit_or_debit_note = "Credit Note" if self.filters.party_type == "Customer" else "Debit Note"

        columns += [
            {
                "label": _("Opening Balance"),
                "fieldname": "opening_balance",
                "fieldtype": "Currency",
                "options": "currency",
                "width": 120,
            },
            {
                "label": _("Invoiced Amount"),
                "fieldname": "invoiced_amount",
                "fieldtype": "Currency",
                "options": "currency",
                "width": 120,
            },
            {
                "label": _("Paid Amount"),
                "fieldname": "paid_amount",
                "fieldtype": "Currency",
                "options": "currency",
                "width": 120,
            },
            {
                "label": _(credit_or_debit_note),
                "fieldname": "return_amount",
                "fieldtype": "Currency",
                "options": "currency",
                "width": 120,
            },
        ]

        for account in self.party_adjustment_accounts:
            columns.append(
                {
                    "label": account,
                    "fieldname": "adj_" + scrub(account),
                    "fieldtype": "Currency",
                    "options": "currency",
                    "width": 120,
                    "is_adjustment": 1,
                }
            )

        columns += [
            {
                "label": _("Closing Balance"),
                "fieldname": "closing_balance",
                "fieldtype": "Currency",
                "options": "currency",
                "width": 120,
            },
            {
                "label": _("Currency"),
                "fieldname": "currency",
                "fieldtype": "Link",
                "options": "Currency",
                "width": 50,
            },
        ]

        # Hidden columns for handling 'User Permissions'
        if self.filters.party_type == "Customer":
            columns += [
                {
                    "label": _("Territory"),
                    "fieldname": "territory",
                    "fieldtype": "Link",
                    "options": "Territory",
                    "hidden": 1,
                },
                {
                    "label": _("Customer Group"),
                    "fieldname": "customer_group",
                    "fieldtype": "Link",
                    "options": "Customer Group",
                    "hidden": 1,
                },
            ]
        else:
            columns += [
                {
                    "label": _("Supplier Group"),
                    "fieldname": "supplier_group",
                    "fieldtype": "Link",
                    "options": "Supplier Group",
                    "hidden": 1,
                }
            ]
        if self.filters.date_wise_bifurcation:
            columns.insert(0, {
                    "label": _("Posting Date"),
                    "fieldname": "posting_date",
                    "fieldtype": "Date",
                    "width": 120,
                },)
        return columns

    def get_data(self):
        company_currency = frappe.get_cached_value("Company", self.filters.get("company"), "default_currency")
        invoice_dr_or_cr = "debit" if self.filters.party_type == "Customer" else "credit"
        reverse_dr_or_cr = "credit" if self.filters.party_type == "Customer" else "debit"

        self.party_data = frappe._dict({})  
        for gle in self.gl_entries:
            if self.filters.get("date_wise_bifurcation"):
                party_posting_key = f"{gle.party}_{gle.posting_date}"
            else:
                party_posting_key = f"{gle.party}"

            self.party_data.setdefault(party_posting_key, frappe._dict({
                "party": gle.party,
                "party_name": gle.party_name,
                "posting_date": gle.posting_date if self.filters.get("date_wise_bifurcation") else None,
                "opening_balance": 0,
                "invoiced_amount": 0,
                "paid_amount": 0,
                "return_amount": 0,
                "closing_balance": 0,
                "currency": company_currency,
            }))

            amount = gle.get(invoice_dr_or_cr) - gle.get(reverse_dr_or_cr)
            party_data = self.party_data[party_posting_key]

            if gle.posting_date < self.filters.from_date or gle.is_opening == "Yes":
                party_data.opening_balance += amount
            else:
                if amount > 0:
                    party_data.invoiced_amount += amount
                elif gle.voucher_no in self.return_invoices:
                    party_data.return_amount -= amount
                else:
                    party_data.paid_amount -= amount

            party_data.closing_balance += amount
            
        out = []
        flag = 1
        opening, close = 0, 0
        for party_posting_key, row in self.party_data.items():
            if "before_" not in party_posting_key:
                if row.opening_balance or row.invoiced_amount or row.paid_amount or row.return_amount or row.closing_balance:
                    total_party_adjustment = sum(amount for amount in self.party_adjustment_details.get(row.party, {}).values())
                    if not self.filters.get("date_wise_bifurcation"):
                        row.paid_amount -= total_party_adjustment
                        adjustments = self.party_adjustment_details.get(row.party, {})
                        for account in self.party_adjustment_accounts:
                            row["adj_" + scrub(account)] = adjustments.get(account, 0)
                    else:
                        if row.paid_amount and flag:
                            row.paid_amount -= total_party_adjustment
                            adjustments = self.party_adjustment_details.get(row.party, {})
                            for account in self.party_adjustment_accounts:
                                row["adj_" + scrub(account)] = adjustments.get(account, 0)
                            flag = 0
                    
                    if self.filters.get("date_wise_bifurcation"):
                        if row.posting_date < self.filters.from_date:
                            opening += row.opening_balance
                            close += row.closing_balance
                        else:
                            out.append(row)
                    else:
                        out.append(row)
        if self.filters.get("date_wise_bifurcation"):
            out.insert(0, {'party': ' ', 'party_name': ' ', 'opening_balance': opening, 'closing_balance': close, 'currency': company_currency})
        return out

    def get_gl_entries(self):
        conditions = self.prepare_conditions()
        join = join_field = ""
        if self.filters.party_type == "Customer":
            join_field = ", p.customer_name as party_name"
            join = "left join `tabCustomer` p on gle.party = p.name"
        elif self.filters.party_type == "Supplier":
            join_field = ", p.supplier_name as party_name"
            join = "left join `tabSupplier` p on gle.party = p.name"

        self.gl_entries = frappe.db.sql(
            f"""
            select
                gle.posting_date, gle.party, gle.voucher_type, gle.voucher_no, gle.against_voucher_type,
                gle.against_voucher, gle.debit, gle.credit, gle.is_opening {join_field}
            from `tabGL Entry` gle
            {join}
            where
                gle.docstatus < 2 and gle.is_cancelled = 0 and gle.party_type=%(party_type)s and ifnull(gle.party, '') != ''
                and gle.posting_date <= %(to_date)s {conditions}
            order by gle.posting_date
            """,
            self.filters,
            as_dict=True,
        )


    def prepare_conditions(self):
        conditions = [""]

        if self.filters.company:
            conditions.append("gle.company=%(company)s")

        if self.filters.finance_book:
            conditions.append("ifnull(finance_book,'') in (%(finance_book)s, '')")

        if self.filters.get("party"):
            conditions.append("party in %(party)s")

        if self.filters.party_type == "Customer":
            if self.filters.get("customer_group"):
                lft, rgt = frappe.db.get_value(
                    "Customer Group", self.filters.get("customer_group"), ["lft", "rgt"]
                )

                conditions.append(
                    f"""party in (select name from tabCustomer
                    where exists(select name from `tabCustomer Group` where lft >= {lft} and rgt <= {rgt}
                        and name=tabCustomer.customer_group))"""
                )

            if self.filters.get("territory"):
                lft, rgt = frappe.db.get_value("Territory", self.filters.get("territory"), ["lft", "rgt"])

                conditions.append(
                    f"""party in (select name from tabCustomer
                    where exists(select name from `tabTerritory` where lft >= {lft} and rgt <= {rgt}
                        and name=tabCustomer.territory))"""
                )

            if self.filters.get("payment_terms_template"):
                conditions.append(
                    "party in (select name from tabCustomer where payment_terms=%(payment_terms_template)s)"
                )

            if self.filters.get("sales_partner"):
                conditions.append(
                    "party in (select name from tabCustomer where default_sales_partner=%(sales_partner)s)"
                )

            if self.filters.get("sales_person"):
                lft, rgt = frappe.db.get_value(
                    "Sales Person", self.filters.get("sales_person"), ["lft", "rgt"]
                )

                conditions.append(
                    """exists(select name from `tabSales Team` steam where
                    steam.sales_person in (select name from `tabSales Person` where lft >= {} and rgt <= {})
                    and ((steam.parent = voucher_no and steam.parenttype = voucher_type)
                        or (steam.parent = against_voucher and steam.parenttype = against_voucher_type)
                        or (steam.parent = party and steam.parenttype = 'Customer')))""".format(lft, rgt)
                )

        if self.filters.party_type == "Supplier":
            if self.filters.get("supplier_group"):
                conditions.append(
                    """party in (select name from tabSupplier
                    where supplier_group=%(supplier_group)s)"""
                )

        return " and ".join(conditions)

    def get_return_invoices(self):
        doctype = "Sales Invoice" if self.filters.party_type == "Customer" else "Purchase Invoice"
        self.return_invoices = [
            d.name
            for d in frappe.get_all(
                doctype,
                filters={
                    "is_return": 1,
                    "docstatus": 1,
                    "posting_date": ["between", [self.filters.from_date, self.filters.to_date]],
                },
            )
        ]

    def get_party_adjustment_amounts(self):
        conditions = self.prepare_conditions()
        account_type = "Expense Account" if self.filters.party_type == "Customer" else "Income Account"
        income_or_expense_accounts = frappe.db.get_all(
            "Account", filters={"account_type": account_type, "company": self.filters.company}, pluck="name"
        )
        invoice_dr_or_cr = "debit" if self.filters.party_type == "Customer" else "credit"
        reverse_dr_or_cr = "credit" if self.filters.party_type == "Customer" else "debit"
        round_off_account = frappe.get_cached_value("Company", self.filters.company, "round_off_account")

        gl = qb.DocType("GL Entry")
        if not income_or_expense_accounts:
            # prevent empty 'in' condition
            income_or_expense_accounts.append("")
        else:
            # escape '%' in account name
            # ignoring frappe.db.escape as it replaces single quotes with double quotes
            income_or_expense_accounts = [x.replace("%", "%%") for x in income_or_expense_accounts]

        accounts_query = (
            qb.from_(gl)
            .select(gl.voucher_type, gl.voucher_no)
            .where(
                (gl.account.isin(income_or_expense_accounts))
                & (gl.posting_date.gte(self.filters.from_date))
                & (gl.posting_date.lte(self.filters.to_date))
            )
        )

        gl_entries = frappe.db.sql(
            f"""
            select
                posting_date, account, party, voucher_type, voucher_no, debit, credit
            from
                `tabGL Entry`
            where
                docstatus < 2 and is_cancelled = 0
                and (voucher_type, voucher_no) in (
                {accounts_query}
                ) and (voucher_type, voucher_no) in (
                    select voucher_type, voucher_no from `tabGL Entry` gle
                    where gle.party_type=%(party_type)s and ifnull(party, '') != ''
                    and gle.posting_date between %(from_date)s and %(to_date)s and gle.docstatus < 2 {conditions}
                )
            """,
            self.filters,
            as_dict=True,
        )

        self.party_adjustment_details = {}
        self.party_adjustment_accounts = set()
        adjustment_voucher_entries = {}
        for gle in gl_entries:
            adjustment_voucher_entries.setdefault((gle.voucher_type, gle.voucher_no), [])
            adjustment_voucher_entries[(gle.voucher_type, gle.voucher_no)].append(gle)

        for voucher_gl_entries in adjustment_voucher_entries.values():
            parties = {}
            accounts = {}
            has_irrelevant_entry = False

            for gle in voucher_gl_entries:
                if gle.account == round_off_account:
                    continue
                elif gle.party:
                    parties.setdefault(gle.party, 0)
                    parties[gle.party] += gle.get(reverse_dr_or_cr) - gle.get(invoice_dr_or_cr)
                elif frappe.get_cached_value("Account", gle.account, "account_type") == account_type:
                    accounts.setdefault(gle.account, 0)
                    accounts[gle.account] += gle.get(invoice_dr_or_cr) - gle.get(reverse_dr_or_cr)
                else:
                    has_irrelevant_entry = True

            if parties and accounts:
                if len(parties) == 1:
                    party = next(iter(parties.keys()))
                    for account, amount in accounts.items():
                        self.party_adjustment_accounts.add(account)
                        self.party_adjustment_details.setdefault(party, {})
                        self.party_adjustment_details[party].setdefault(account, 0)
                        self.party_adjustment_details[party][account] += amount
                elif len(accounts) == 1 and not has_irrelevant_entry:
                    account = next(iter(accounts.keys()))
                    self.party_adjustment_accounts.add(account)
                    for party, amount in parties.items():
                        self.party_adjustment_details.setdefault(party, {})
                        self.party_adjustment_details[party].setdefault(account, 0)
                        self.party_adjustment_details[party][account] += amount


def execute(filters=None):
    args = {
        "party_type": "Customer",
        "naming_by": ["Selling Settings", "cust_master_name"],
    }
    mode_of_payment_filter = filters.get('mode_of_payment') or []
    party_filter = filters.get('party') or None
    party_group_filter = filters.get('party_group') or None

    report = PartyLedgerSummaryReport(filters)
    columns, data = report.run(args)
    
    new_columns = [
        {'label': 'Credit Limit', 'fieldname': 'credit_limit', 'fieldtype': 'Currency', 'options': 'currency', 'width': 120},
        {'label': 'Cash Receipts', 'fieldname': 'cash_amount', 'fieldtype': 'Currency', 'options': 'currency', 'width': 120},
        {'label': 'Bank Receipts', 'fieldname': 'bank_amount', 'fieldtype': 'Currency', 'options': 'currency', 'width': 120}
    ]
    columns.insert(1, {"label": "Customer Name", "fieldtype": "Data", "fieldname": "party_naming", "width": 200})
    columns.extend(new_columns)
    
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    company = filters.get('company')
    
    if filters.date_wise_bifurcation:
        data = add_receipts_data_bifurcation(data, from_date, to_date, mode_of_payment_filter, company, party_filter, party_group_filter)
    else:
        data = add_receipts_data(data, from_date, to_date, mode_of_payment_filter, company, party_filter, party_group_filter)
    
    return columns, data


def add_receipts_data_bifurcation(data, from_date, to_date, mode_of_payment_filter, company, party_filter=None, party_group_filter=None):
    mode_of_payment_conditions = ''
    if mode_of_payment_filter:
        placeholders = ', '.join(['%s'] * len(mode_of_payment_filter))
        mode_of_payment_conditions = f"AND mode_of_payment IN ({placeholders})"

    # Add party and party_group filters
    party_conditions = ''
    if party_filter:
        party_conditions += f"AND party = %s "
    if party_group_filter:
        party_conditions += f"AND party IN (SELECT name FROM `tabCustomer` WHERE customer_group = %s) "

    # Fetch bank and cash entries
    bank_entries = frappe.db.sql(f"""
        SELECT party, SUM(paid_amount) AS total_paid, posting_date
        FROM `tabPayment Entry`
        WHERE posting_date BETWEEN %s AND %s
        AND payment_type = 'Receive' AND docstatus = 1
        AND mod_type = 'Bank'
        {mode_of_payment_conditions}
        {party_conditions}
        GROUP BY party, posting_date
    """, (from_date, to_date) + tuple(mode_of_payment_filter) + ((party_filter,) if party_filter else ()) + ((party_group_filter,) if party_group_filter else ()), as_dict=True)

    cash_entries = frappe.db.sql(f"""
        SELECT party, SUM(paid_amount) AS total_paid, posting_date
        FROM `tabPayment Entry`
        WHERE posting_date BETWEEN %s AND %s
        AND payment_type = 'Receive' AND docstatus = 1
        AND mod_type = 'Cash'
        {mode_of_payment_conditions}
        {party_conditions}
        GROUP BY party, posting_date
    """, (from_date, to_date) + tuple(mode_of_payment_filter) + ((party_filter,) if party_filter else ()) + ((party_group_filter,) if party_group_filter else ()), as_dict=True)

    # frappe.throw(f"{bank_entries}  === {cash_entries}")
    bank_receipts = {(entry['party'], entry['posting_date']): entry['total_paid'] for entry in bank_entries}
    cash_receipts = {(entry['party'], entry['posting_date']): entry['total_paid'] for entry in cash_entries}

    # Update data rows
    for row in data:
        party = row.get('party')
        posting_date = row.get('posting_date')
        row['bank_amount'] = bank_receipts.get((party, posting_date), 0.0)
        row['cash_amount'] = cash_receipts.get((party, posting_date), 0.0)
        row['party_naming'] = frappe.db.get_value("Customer", party, "customer_name")

    # Add credit limits
    credit_limit_cache = {}
    previous = None

    for row in data:
        current = row['party']
        if current != previous:
            if current not in credit_limit_cache:
                credit_limit_cache[current] = frappe.db.get_value(
                    "Customer Credit Limit", 
                    {"parent": current, "company": company}, 
                    "credit_limit"
                )
            row['credit_limit'] = credit_limit_cache[current]
            previous = current
        else:
            row['credit_limit'] = 0

    return data


def add_receipts_data(data, from_date, to_date, mode_of_payment_filter, company, party_filter=None, party_group_filter=None):
    mode_of_payment_conditions = ''
    if mode_of_payment_filter:
        placeholders = ', '.join(['%s'] * len(mode_of_payment_filter))
        mode_of_payment_conditions = f"AND mode_of_payment IN ({placeholders})"

    # Add party and party_group filters
    party_conditions = ''
    if party_filter:
        party_conditions += f"AND party IN %s "
    if party_group_filter:
        party_conditions += f"AND party IN (SELECT name FROM `tabCustomer` WHERE customer_group = %s) "

    # Fetch bank and cash entries
    bank_entries = frappe.db.sql(f"""
        SELECT party, SUM(paid_amount) AS total_paid
        FROM `tabPayment Entry`
        WHERE posting_date BETWEEN %s AND %s
        AND payment_type = 'Receive' AND docstatus = 1
        AND mod_type = 'Bank'
        {mode_of_payment_conditions}
        {party_conditions}
        GROUP BY party
    """, (from_date, to_date) + tuple(mode_of_payment_filter) + ((party_filter,) if party_filter else ()) + ((party_group_filter,) if party_group_filter else ()), as_dict=True)

    cash_entries = frappe.db.sql(f"""
        SELECT party, SUM(paid_amount) AS total_paid
        FROM `tabPayment Entry`
        WHERE posting_date BETWEEN %s AND %s
        AND payment_type = 'Receive' AND docstatus = 1
        AND mod_type = 'Cash'
        {mode_of_payment_conditions}
        {party_conditions}
        GROUP BY party
    """, (from_date, to_date) + tuple(mode_of_payment_filter) + ((party_filter,) if party_filter else ()) + ((party_group_filter,) if party_group_filter else ()), as_dict=True)

    bank_receipts = {entry['party']: entry['total_paid'] for entry in bank_entries}
    cash_receipts = {entry['party']: entry['total_paid'] for entry in cash_entries}

    # Update data rows
    for row in data:
        party = row.get('party')
        row['cash_amount'] = cash_receipts.get(party, 0.0)
        row['bank_amount'] = bank_receipts.get(party, 0.0)
        row['party_naming'] = frappe.db.get_value("Customer", party, "customer_name")
        row['credit_limit'] = frappe.db.get_value("Customer Credit Limit", {"parent": party, "company": company}, "credit_limit")

    return data
