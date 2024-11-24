import frappe
from datetime import datetime

def execute(filters=None):
    columns = [
        {"label": "DCS", "fieldname": "dcs", "fieldtype": "Link", "options": "Warehouse"},
        {"label": "ACK LITER", "fieldname": "ack_liter", "fieldtype": "Float", "width": 120},
        {"label": "ACK KG", "fieldname": "ack_kg", "fieldtype": "Float", "width": 120},
        {"label": "ACK FAT", "fieldname": "ack_fat", "fieldtype": "Float", "width": 120},
        {"label": "ACK SNF", "fieldname": "ack_snf", "fieldtype": "Float", "width": 120},
        {"label": "ACK KG FAT", "fieldname": "ack_kg_fat", "fieldtype": "Float", "width": 120},
        {"label": "ACK KG SNF", "fieldname": "ack_kg_snf", "fieldtype": "Float", "width": 120},
        {"label": "REC LITER", "fieldname": "rec_liter", "fieldtype": "Float", "width": 120},
        {"label": "REC KG", "fieldname": "rec_kg", "fieldtype": "Float", "width": 120},
        {"label": "REC FAT", "fieldname": "rec_fat", "fieldtype": "Float", "width": 120},
        {"label": "REC SNF", "fieldname": "rec_snf", "fieldtype": "Float", "width": 120},
        {"label": "REC KG FAT", "fieldname": "rec_kg_fat", "fieldtype": "Float", "width": 120},
        {"label": "REC KG SNF", "fieldname": "rec_kg_snf", "fieldtype": "Float", "width": 120},
        {"label": "DIFF LITER", "fieldname": "diff_liter", "fieldtype": "Float", "width": 120},
        {"label": "DIFF KG", "fieldname": "diff_kg", "fieldtype": "Float", "width": 120},
        {"label": "DIFF FAT", "fieldname": "diff_fat", "fieldtype": "Float", "width": 120},
        {"label": "DIFF SNF", "fieldname": "diff_snf", "fieldtype": "Float", "width": 120},
        {"label": "DIFF KG FAT", "fieldname": "diff_kg_fat", "fieldtype": "Float", "width": 120},
        {"label": "DIFF KG SNF", "fieldname": "diff_kg_snf", "fieldtype": "Float", "width": 120},
    ]

    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    from_shift = filters.get('from_shift')
    to_shift = filters.get('to_shift')
    dcs_filter = filters.get('dcs')

    from_date = datetime.strptime(from_date, '%Y-%m-%d')
    to_date = datetime.strptime(to_date, '%Y-%m-%d')

    if to_shift == "Morning":
        to_shift_condition = "AND tme.shift = 'Morning'"
    else: 
        to_shift_condition = "AND tme.shift IN ('Morning', 'Evening')"

    if not isinstance(dcs_filter, list):
        dcs_filter = [dcs_filter] if dcs_filter else []

    tank_condition = " AND tio.dcs IN ({})".format(', '.join(['%s'] * len(dcs_filter))) if dcs_filter else ""

    tank_sql_query = """
        SELECT 
            tio.dcs as dcs,
            tio.name as name,
            COALESCE(SUM(tid.quantity), 0) as rec_liter, 
            COALESCE(SUM(tid.quantity_kg), 0) as rec_kg, 
            COALESCE(AVG(tid.fat_), 0) as rec_fat, 
            COALESCE(AVG(tid.snf_), 0) as rec_snf,
            COALESCE(SUM((tid.quantity_kg * tid.fat_)/100), 0) as rec_kg_fat, 
            COALESCE(SUM((tid.quantity_kg * tid.snf_)/100), 0) as rec_kg_snf,
            tme.date as milk_entry_date,
            tme.shift as milk_entry_shift
        FROM
            `tabTanker Inward Outward` tio
        LEFT JOIN
            `tabTanker Inward Divison` tid ON tid.parent = tio.name
        LEFT JOIN
            `tabTanker Milk Entry Details` tme ON tme.parent = tio.name
        WHERE 
            tio.date BETWEEN %s AND %s
            AND tio.docstatus = 1
            {to_shift_condition}
            {tank_condition}
        GROUP BY 
            tio.dcs, tme.date, tme.shift
    """.format(
        to_shift_condition=to_shift_condition, 
        tank_condition=tank_condition
    )

    tank_params = [from_date, to_date] + dcs_filter
    tank_data = frappe.db.sql(tank_sql_query, tuple(tank_params), as_dict=True)

    result_dict = {}

    for tank in tank_data:
        milk_entry_sql_query = """
            SELECT 
                dcs_id as dcs, 
                SUM(volume) as ack_liter,
                SUM(volume*1.03) as ack_kg,
                AVG(fat) as ack_fat, 
                AVG(snf) as ack_snf,
                SUM(fat_kg) as ack_kg_fat, 
                SUM(snf_kg) as ack_kg_snf
            FROM 
                `tabMilk Entry`
            WHERE 
                dcs_id = %s
                AND date = %s
                AND shift = %s
                AND docstatus = 1
            GROUP BY 
                dcs_id
        """
        milk_params = [tank['dcs'], tank['milk_entry_date'], tank['milk_entry_shift']]
        milk_data = frappe.db.sql(milk_entry_sql_query, tuple(milk_params), as_dict=True)

        milk_entry = milk_data[0] if milk_data else {}

        if tank['dcs'] not in result_dict:
            result_dict[tank['dcs']] = {
                "name": tank['name'],
                "dcs": tank['dcs'],
                "ack_liter": milk_entry.get('ack_liter', 0),
                "ack_kg": milk_entry.get('ack_kg', 0),
                "ack_fat": milk_entry.get('ack_fat', 0),
                "ack_snf": milk_entry.get('ack_snf', 0),
                "ack_kg_fat": milk_entry.get('ack_kg_fat', 0),
                "ack_kg_snf": milk_entry.get('ack_kg_snf', 0),
                "rec_liter": tank['rec_liter'],
                "rec_kg": tank['rec_kg'],
                "rec_fat": tank['rec_fat'],
                "rec_snf": tank['rec_snf'],
                "rec_kg_fat": tank['rec_kg_fat'],
                "rec_kg_snf": tank['rec_kg_snf'],
                "diff_liter": tank['rec_liter'] - milk_entry.get('ack_liter', 0),
                "diff_kg": tank['rec_kg'] - milk_entry.get('ack_kg', 0),
                "diff_fat": tank['rec_fat'] - milk_entry.get('ack_fat', 0),
                "diff_snf": tank['rec_snf'] - milk_entry.get('ack_snf', 0),
                "diff_kg_fat": tank['rec_kg_fat'] - milk_entry.get('ack_kg_fat', 0),
                "diff_kg_snf": tank['rec_kg_snf'] - milk_entry.get('ack_kg_snf', 0)
            }
        else:
            if tank['name'] == result_dict[tank['dcs']]['name']:
                result = result_dict[tank['dcs']]
                result["ack_liter"] += milk_entry.get('ack_liter', 0)
                result["ack_kg"] += milk_entry.get('ack_kg', 0)
                result["ack_fat"] = (result["ack_fat"] + milk_entry.get('ack_fat', 0))/2
                result["ack_snf"] = (result["ack_snf"] + milk_entry.get('ack_snf', 0))/2
                result["ack_kg_fat"] += ((milk_entry.get('ack_kg', 0) * milk_entry.get('ack_kg_fat', 0))/100)
                result["ack_kg_snf"] += ((milk_entry.get('ack_kg', 0) * milk_entry.get('ack_kg_snf', 0))/100)
                result["diff_liter"] = result["rec_liter"] - result["ack_liter"]
                result["diff_kg"] = result["rec_kg"] - result["ack_kg"]
                result["diff_fat"] = result["rec_fat"] - result["ack_fat"]
                result["diff_snf"] = result["rec_snf"] - result["ack_snf"]
                result["diff_kg_fat"] = result["rec_kg_fat"] - result["ack_kg_fat"]
                result["diff_kg_snf"] = result["rec_kg_snf"] - result["ack_kg_snf"]
            else:
                if tank['dcs'] in result_dict and tank['name'] not in result_dict:
                    result_dict[tank['dcs']]['name'] = tank['name']
                    result_dict[tank['dcs']]["rec_liter"] += tank['rec_liter']
                    result_dict[tank['dcs']]["rec_kg"] += tank['rec_kg']
                    result_dict[tank['dcs']]["rec_fat"] = (result_dict[tank['dcs']]["rec_fat"] + tank['rec_fat'])/2
                    result_dict[tank['dcs']]["rec_snf"] = (result_dict[tank['dcs']]["rec_snf"] +tank['rec_snf'])/2
                    result_dict[tank['dcs']]["rec_kg_fat"] += ((tank['rec_kg'] * tank['rec_kg_fat'])/100)
                    result_dict[tank['dcs']]["rec_kg_snf"] += ((tank['rec_kg'] * tank['rec_kg_snf'])/100)
                    result_dict[tank['dcs']]["ack_liter"] += milk_entry.get('ack_liter', 0)
                    result_dict[tank['dcs']]["ack_kg"] += milk_entry.get('ack_kg', 0)
                    result_dict[tank['dcs']]["ack_fat"] += milk_entry.get('ack_fat', 0)
                    result_dict[tank['dcs']]["ack_snf"] += milk_entry.get('ack_snf', 0)
                    result_dict[tank['dcs']]["ack_kg_fat"] += milk_entry.get('ack_kg_fat', 0)
                    result_dict[tank['dcs']]["ack_kg_snf"] += milk_entry.get('ack_kg_snf', 0)
                    result_dict[tank['dcs']]["diff_liter"] = result_dict[tank['dcs']]["rec_liter"] - result_dict[tank['dcs']]["ack_liter"]
                    result_dict[tank['dcs']]["diff_kg"] = result_dict[tank['dcs']]["rec_kg"] - result_dict[tank['dcs']]["ack_kg"]
                    result_dict[tank['dcs']]["diff_fat"] = result_dict[tank['dcs']]["rec_fat"] - result_dict[tank['dcs']]["ack_fat"]
                    result_dict[tank['dcs']]["diff_snf"] = result_dict[tank['dcs']]["rec_snf"] - result_dict[tank['dcs']]["ack_snf"]
                    result_dict[tank['dcs']]["diff_kg_fat"] = result_dict[tank['dcs']]["rec_kg_fat"] - result_dict[tank['dcs']]["ack_kg_fat"]
                    result_dict[tank['dcs']]["diff_kg_snf"] = result_dict[tank['dcs']]["rec_kg_snf"] - result_dict[tank['dcs']]["ack_kg_snf"]

    result = list(result_dict.values())

    return columns, result





# import frappe
# from datetime import datetime, timedelta

# def execute(filters=None):
#     columns = [
#         {"label": "DCS", "fieldname": "dcs", "fieldtype": "Link", "options": "Warehouse"},
#         {"label": "ACK LITER", "fieldname": "ack_liter", "fieldtype": "Float", "width": 120},
#         {"label": "ACK KG", "fieldname": "ack_kg", "fieldtype": "Float", "width": 120},
#         {"label": "ACK FAT", "fieldname": "ack_fat", "fieldtype": "Float", "width": 120},
#         {"label": "ACK SNF", "fieldname": "ack_snf", "fieldtype": "Float", "width": 120},
#         {"label": "ACK KG FAT", "fieldname": "ack_kg_fat", "fieldtype": "Float", "width": 120},
#         {"label": "ACK KG SNF", "fieldname": "ack_kg_snf", "fieldtype": "Float", "width": 120},
#         {"label": "REC LITER", "fieldname": "rec_liter", "fieldtype": "Float", "width": 120},
#         {"label": "REC KG", "fieldname": "rec_kg", "fieldtype": "Float", "width": 120},
#         {"label": "REC FAT", "fieldname": "rec_fat", "fieldtype": "Float", "width": 120},
#         {"label": "REC SNF", "fieldname": "rec_snf", "fieldtype": "Float", "width": 120},
#         {"label": "REC KG FAT", "fieldname": "rec_kg_fat", "fieldtype": "Float", "width": 120},
#         {"label": "REC KG SNF", "fieldname": "rec_kg_snf", "fieldtype": "Float", "width": 120},
#         {"label": "DIFF LITER", "fieldname": "diff_liter", "fieldtype": "Float", "width": 120},
#         {"label": "DIFF KG", "fieldname": "diff_kg", "fieldtype": "Float", "width": 120},
#         {"label": "DIFF FAT", "fieldname": "diff_fat", "fieldtype": "Float", "width": 120},
#         {"label": "DIFF SNF", "fieldname": "diff_snf", "fieldtype": "Float", "width": 120},
#         {"label": "DIFF KG FAT", "fieldname": "diff_kg_fat", "fieldtype": "Float", "width": 120},
#         {"label": "DIFF KG SNF", "fieldname": "diff_kg_snf", "fieldtype": "Float", "width": 120},
#     ]

#     from_date = filters.get('from_date')
#     to_date = filters.get('to_date')
#     from_shift = filters.get('from_shift')
#     to_shift = filters.get('to_shift')
#     dcs_filter = filters.get('dcs')

#     from_date = datetime.strptime(from_date, '%Y-%m-%d')
#     to_date = datetime.strptime(to_date, '%Y-%m-%d')
    
#     # Shift conditions
#     if from_shift == "Morning":
#         from_shift_condition = "AND shift IN ('Morning', 'Evening')"
#     else:  # Evening
#         from_shift_condition = "AND shift = 'Evening'"
    
#     if to_shift == "Morning":
#         to_shift_condition = "AND shift = 'Morning'"
#     else:  # Evening
#         to_shift_condition = "AND shift IN ('Morning', 'Evening')"

#     if not isinstance(dcs_filter, list):
#         dcs_filter = [dcs_filter] if dcs_filter else []

#     dcs_condition = " AND dcs_id IN ({})".format(', '.join(['%s'] * len(dcs_filter))) if dcs_filter else ""
#     tank_condition = " AND tio.dcs IN ({})".format(', '.join(['%s'] * len(dcs_filter))) if dcs_filter else ""

#     milk_entry_sql_query = """
#         SELECT 
#             dcs_id as dcs, 
#             SUM(volume) as ack_liter,
#             SUM(volume*1.03) as ack_kg,
#             AVG(fat) as ack_fat, 
#             AVG(snf) as ack_snf,
#             SUM(fat_kg) as ack_kg_fat, 
#             SUM(snf_kg) as ack_kg_snf
#         FROM 
#             `tabMilk Entry`
#         WHERE 
#             date BETWEEN %s AND %s
#             AND docstatus = 1
#             {from_shift_condition}
#             {dcs_condition}
#         GROUP BY 
#             dcs_id
#     """.format(from_shift_condition=from_shift_condition, dcs_condition=dcs_condition)

#     milk_params = [from_date, to_date] + dcs_filter
    
#     milk_data = frappe.db.sql(milk_entry_sql_query, tuple(milk_params), as_dict=True)

#     tank_sql_query = """
#         SELECT 
#             tio.dcs as dcs, 
#             tio.name as name, 
#             COALESCE(SUM(tid.quantity), 0) as rec_liter, 
#             COALESCE(SUM(tid.quantity_kg), 0) as rec_kg, 
#             COALESCE(AVG(tid.fat_), 0) as rec_fat, 
#             COALESCE(AVG(tid.snf_), 0) as rec_snf,
#             COALESCE(SUM((tid.quantity_kg * tid.fat_)/100), 0) as rec_kg_fat, 
#             COALESCE(SUM((tid.quantity_kg * tid.snf_)/100), 0) as rec_kg_snf
#         FROM
#             `tabTanker Inward Outward` tio
#         LEFT JOIN
#             `tabTanker Inward Divison` tid ON tid.parent = tio.name
#         WHERE 
#             tio.date BETWEEN %s AND %s
#             AND tio.docstatus = 1
#             {to_shift_condition}
#             {tank_condition}
#         GROUP BY 
#             tio.dcs
#     """.format(to_shift_condition=to_shift_condition, tank_condition=tank_condition)
#     tank_params = [from_date, to_date] + dcs_filter
#     tank_data = frappe.db.sql(tank_sql_query, tuple(tank_params), as_dict=True)
#     frappe.msgprint(str(tank_data))
    
#     milk_dict = {item['dcs']: item for item in milk_data}
#     tank_dict = {item['dcs']: item for item in tank_data}
    
#     result = []
    
#     for dcs in set(milk_dict.keys()).union(tank_dict.keys()):
#         milk_entry = milk_dict.get(dcs, {})
#         tanker_entry = tank_dict.get(dcs, {})
        
#         result.append({
#             "dcs": dcs,
#             "ack_liter": milk_entry.get('ack_liter', 0),
#             "ack_kg": milk_entry.get('ack_kg', 0),
#             "ack_fat": milk_entry.get('ack_fat', 0),
#             "ack_snf": milk_entry.get('ack_snf', 0),
#             "ack_kg_fat": milk_entry.get('ack_kg_fat', 0),
#             "ack_kg_snf": milk_entry.get('ack_kg_snf', 0),
#             "rec_liter": tanker_entry.get('rec_liter', 0),
#             "rec_kg": tanker_entry.get('rec_kg', 0),
#             "rec_fat": tanker_entry.get('rec_fat', 0),
#             "rec_snf": tanker_entry.get('rec_snf', 0),
#             "rec_kg_fat": tanker_entry.get('rec_kg_fat', 0),
#             "rec_kg_snf": tanker_entry.get('rec_kg_snf', 0),
#             "diff_liter": milk_entry.get('ack_liter', 0) - tanker_entry.get('rec_liter', 0),
#             "diff_kg": milk_entry.get('ack_kg', 0) - tanker_entry.get('rec_kg', 0),
#             "diff_fat": milk_entry.get('ack_fat', 0) - tanker_entry.get('rec_fat', 0),
#             "diff_snf": milk_entry.get('ack_snf', 0) - tanker_entry.get('rec_snf', 0),
#             "diff_kg_fat": milk_entry.get('ack_kg_fat', 0) - tanker_entry.get('rec_kg_fat', 0),
#             "diff_kg_snf": milk_entry.get('ack_kg_snf', 0) - tanker_entry.get('rec_kg_snf', 0),
#         })
    
#     return columns, result






# import frappe
# from datetime import datetime

# def execute(filters=None):
#     columns = [
#         {"label": "DCS", "fieldname": "dcs", "fieldtype": "Link", "options": "Warehouse"},
#         {"label": "ACK LITER", "fieldname": "ack_liter", "fieldtype": "Float", "width": 120},
#         {"label": "ACK KG", "fieldname": "ack_kg", "fieldtype": "Float", "width": 120},
#         {"label": "ACK FAT", "fieldname": "ack_fat", "fieldtype": "Float", "width": 120},
#         {"label": "ACK SNF", "fieldname": "ack_snf", "fieldtype": "Float", "width": 120},
#         {"label": "ACK KG FAT", "fieldname": "ack_kg_fat", "fieldtype": "Float", "width": 120},
#         {"label": "ACK KG SNF", "fieldname": "ack_kg_snf", "fieldtype": "Float", "width": 120},
#         {"label": "REC LITER", "fieldname": "rec_liter", "fieldtype": "Float", "width": 120},
#         {"label": "REC KG", "fieldname": "rec_kg", "fieldtype": "Float", "width": 120},
#         {"label": "REC FAT", "fieldname": "rec_fat", "fieldtype": "Float", "width": 120},
#         {"label": "REC SNF", "fieldname": "rec_snf", "fieldtype": "Float", "width": 120},
#         {"label": "REC KG FAT", "fieldname": "rec_kg_fat", "fieldtype": "Float", "width": 120},
#         {"label": "REC KG SNF", "fieldname": "rec_kg_snf", "fieldtype": "Float", "width": 120},
#         {"label": "DIFF LITER", "fieldname": "diff_liter", "fieldtype": "Float", "width": 120},
#         {"label": "DIFF KG", "fieldname": "diff_kg", "fieldtype": "Float", "width": 120},
#         {"label": "DIFF FAT", "fieldname": "diff_fat", "fieldtype": "Float", "width": 120},
#         {"label": "DIFF SNF", "fieldname": "diff_snf", "fieldtype": "Float", "width": 120},
#         {"label": "DIFF KG FAT", "fieldname": "diff_kg_fat", "fieldtype": "Float", "width": 120},
#         {"label": "DIFF KG SNF", "fieldname": "diff_kg_snf", "fieldtype": "Float", "width": 120},
#     ]

#     from_date = filters.get('from_date')
#     to_date = filters.get('to_date')
#     from_shift = filters.get('from_shift')
#     to_shift = filters.get('to_shift')
#     dcs_filter = filters.get('dcs')

#     from_date = datetime.strptime(from_date, '%Y-%m-%d')
#     to_date = datetime.strptime(to_date, '%Y-%m-%d')

#     if to_shift == "Morning":
#         to_shift_condition = "AND tme.shift = 'Morning'"
#     else:  # Evening
#         to_shift_condition = "AND tme.shift IN ('Morning', 'Evening')"

#     if not isinstance(dcs_filter, list):
#         dcs_filter = [dcs_filter] if dcs_filter else []

#     tank_condition = " AND tio.dcs IN ({})".format(', '.join(['%s'] * len(dcs_filter))) if dcs_filter else ""

#     tank_sql_query = """
#         SELECT 
#             tio.dcs as dcs,
#             tio.name as name,
#             COALESCE(SUM(tid.quantity), 0) as rec_liter, 
#             COALESCE(SUM(tid.quantity_kg), 0) as rec_kg, 
#             COALESCE(AVG(tid.fat_), 0) as rec_fat, 
#             COALESCE(AVG(tid.snf_), 0) as rec_snf,
#             COALESCE(SUM((tid.quantity_kg * tid.fat_)/100), 0) as rec_kg_fat, 
#             COALESCE(SUM((tid.quantity_kg * tid.snf_)/100), 0) as rec_kg_snf,
#             tme.date as milk_entry_date,
#             tme.shift as milk_entry_shift
#         FROM
#             `tabTanker Inward Outward` tio
#         LEFT JOIN
#             `tabTanker Inward Divison` tid ON tid.parent = tio.name
#         LEFT JOIN
#             `tabTanker Milk Entry Details` tme ON tme.parent = tio.name
#         WHERE 
#             tio.date BETWEEN %s AND %s
#             AND tio.docstatus = 1
#             {to_shift_condition}
#             {tank_condition}
#         GROUP BY 
#             tio.dcs, tme.date, tme.shift
#     """.format(
#         to_shift_condition=to_shift_condition, 
#         tank_condition=tank_condition
#     )

#     tank_params = [from_date, to_date] + dcs_filter
#     tank_data = frappe.db.sql(tank_sql_query, tuple(tank_params), as_dict=True)

#     result_dict = {}
    
#     # Collect and aggregate tank data
#     for tank in tank_data:
#         milk_entry_sql_query = """
#             SELECT 
#                 dcs_id as dcs, 
#                 SUM(volume) as ack_liter,
#                 SUM(volume*1.03) as ack_kg,
#                 AVG(fat) as ack_fat, 
#                 AVG(snf) as ack_snf,
#                 SUM(fat_kg) as ack_kg_fat, 
#                 SUM(snf_kg) as ack_kg_snf
#             FROM 
#                 `tabMilk Entry`
#             WHERE 
#                 dcs_id = %s
#                 AND date = %s
#                 AND shift = %s
#                 AND docstatus = 1
#             GROUP BY 
#                 dcs_id
#         """
#         milk_params = [tank['dcs'], tank['milk_entry_date'], tank['milk_entry_shift']]
#         milk_data = frappe.db.sql(milk_entry_sql_query, tuple(milk_params), as_dict=True)

#         milk_entry = milk_data[0] if milk_data else {}

#         if tank['dcs'] not in result_dict:
#             result_dict[tank['dcs']] = {
#                 "name": tank['name'],
#                 "dcs": tank['dcs'],
#                 "ack_liter": milk_entry.get('ack_liter', 0),
#                 "ack_kg": milk_entry.get('ack_kg', 0),
#                 "ack_fat": milk_entry.get('ack_fat', 0),
#                 "ack_snf": milk_entry.get('ack_snf', 0),
#                 "ack_kg_fat": milk_entry.get('ack_kg_fat', 0),
#                 "ack_kg_snf": milk_entry.get('ack_kg_snf', 0),
#                 "rec_liter": tank['rec_liter'],
#                 "rec_kg": tank['rec_kg'],
#                 "rec_fat": tank['rec_fat'],
#                 "rec_snf": tank['rec_snf'],
#                 "rec_kg_fat": tank['rec_kg_fat'],
#                 "rec_kg_snf": tank['rec_kg_snf'],
#                 "diff_liter": tank['rec_liter'] - milk_entry.get('ack_liter', 0),
#                 "diff_kg": tank['rec_kg'] - milk_entry.get('ack_kg', 0),
#                 "diff_fat": tank['rec_fat'] - milk_entry.get('ack_fat', 0),
#                 "diff_snf": tank['rec_snf'] - milk_entry.get('ack_snf', 0),
#                 "diff_kg_fat": tank['rec_kg_fat'] - milk_entry.get('ack_kg_fat', 0),
#                 "diff_kg_snf": tank['rec_kg_snf'] - milk_entry.get('ack_kg_snf', 0)
#             }
#         else:
#             if result_dict[tank['dcs']]["name"] not in result_dict:
#                 result_dict[tank['dcs']]["ack_liter"] += milk_entry.get('ack_liter', 0)
#                 result_dict[tank['dcs']]["ack_kg"] += milk_entry.get('ack_kg', 0)
#                 result_dict[tank['dcs']]["ack_fat"] += milk_entry.get('ack_fat', 0)
#                 result_dict[tank['dcs']]["ack_snf"] += milk_entry.get('ack_snf', 0)
#                 result_dict[tank['dcs']]["ack_kg_fat"] += milk_entry.get('ack_kg_fat', 0)
#                 result_dict[tank['dcs']]["ack_kg_snf"] += milk_entry.get('ack_kg_snf', 0)
#                 result_dict[tank['dcs']]["rec_liter"] = tank['rec_liter']
#                 result_dict[tank['dcs']]["rec_kg"] = tank['rec_kg']
#                 result_dict[tank['dcs']]["rec_fat"] = tank['rec_fat']
#                 result_dict[tank['dcs']]["rec_snf"] = tank['rec_snf']
#                 result_dict[tank['dcs']]["rec_kg_fat"] = tank['rec_kg_fat']
#                 result_dict[tank['dcs']]["rec_kg_snf"] = tank['rec_kg_snf']
#                 result_dict[tank['dcs']]["diff_liter"] = result_dict[tank['dcs']]["rec_liter"] - result_dict[tank['dcs']]["ack_liter"]
#                 result_dict[tank['dcs']]["diff_kg"] = result_dict[tank['dcs']]["rec_kg"] - result_dict[tank['dcs']]["ack_kg"]
#                 result_dict[tank['dcs']]["diff_fat"] = result_dict[tank['dcs']]["rec_fat"] - result_dict[tank['dcs']]["ack_fat"]
#                 result_dict[tank['dcs']]["diff_snf"] = result_dict[tank['dcs']]["rec_snf"] - result_dict[tank['dcs']]["ack_snf"]
#                 result_dict[tank['dcs']]["diff_kg_fat"] = result_dict[tank['dcs']]["rec_kg_fat"] - result_dict[tank['dcs']]["ack_kg_fat"]
#                 result_dict[tank['dcs']]["diff_kg_snf"] = result_dict[tank['dcs']]["rec_kg_snf"] - result_dict[tank['dcs']]["ack_kg_snf"]
#             else:
#                 frappe.msgprint(str(tank['name']))
#                 result_dict[tank['dcs']]["ack_liter"] = milk_entry.get('ack_liter', 0)
#                 result_dict[tank['dcs']]["ack_kg"] = milk_entry.get('ack_kg', 0)
#                 result_dict[tank['dcs']]["ack_fat"] = milk_entry.get('ack_fat', 0)
#                 result_dict[tank['dcs']]["ack_snf"] = milk_entry.get('ack_snf', 0)
#                 result_dict[tank['dcs']]["ack_kg_fat"] = milk_entry.get('ack_kg_fat', 0)
#                 result_dict[tank['dcs']]["ack_kg_snf"] = milk_entry.get('ack_kg_snf', 0)
#                 result_dict[tank['dcs']]["rec_liter"] += tank['rec_liter']
#                 result_dict[tank['dcs']]["rec_kg"] += tank['rec_kg']
#                 result_dict[tank['dcs']]["rec_fat"] += tank['rec_fat']
#                 result_dict[tank['dcs']]["rec_snf"] += tank['rec_snf']
#                 result_dict[tank['dcs']]["rec_kg_fat"] += tank['rec_kg_fat']
#                 result_dict[tank['dcs']]["rec_kg_snf"] += tank['rec_kg_snf']
#                 result_dict[tank['dcs']]["diff_liter"] = result_dict[tank['dcs']]["rec_liter"] - result_dict[tank['dcs']]["ack_liter"]
#                 result_dict[tank['dcs']]["diff_kg"] = result_dict[tank['dcs']]["rec_kg"] - result_dict[tank['dcs']]["ack_kg"]
#                 result_dict[tank['dcs']]["diff_fat"] = result_dict[tank['dcs']]["rec_fat"] - result_dict[tank['dcs']]["ack_fat"]
#                 result_dict[tank['dcs']]["diff_snf"] = result_dict[tank['dcs']]["rec_snf"] - result_dict[tank['dcs']]["ack_snf"]
#                 result_dict[tank['dcs']]["diff_kg_fat"] = result_dict[tank['dcs']]["rec_kg_fat"] - result_dict[tank['dcs']]["ack_kg_fat"]
#                 result_dict[tank['dcs']]["diff_kg_snf"] = result_dict[tank['dcs']]["rec_kg_snf"] - result_dict[tank['dcs']]["ack_kg_snf"]

#     result = list(result_dict.values())

#     return columns, result