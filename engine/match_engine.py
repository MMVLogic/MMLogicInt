import numpy as np
from scipy.optimize import linear_sum_assignment

def audit_shipment_graph(invoice_data: dict, bol_data: dict, weight_tolerance=0.05):
    """
    Executes a Weighted Bipartite Graph Matching over document line items.
    Handles 'Many-to-One' consolidation scenarios for asymmetric documents.
    """
    invoice_items = invoice_data.get("items", [])
    bol_items = bol_data.get("items", [])
    
    def clean_num(val):
        if val is None: return 0.0
        if isinstance(val, (int, float)): return float(val)
        try:
            import re
            s = str(val).replace(',', '').replace(' ', '').strip()
            match = re.search(r"[-+]?\d*\.?\d+", s)
            if match:
                return float(match.group())
            return 0.0
        except:
            return 0.0

    def get_w(item):
        return clean_num(item.get('gross_weight_kg') or item.get('gross_kg') or item.get('weight_kg') or item.get('weight'))

    # Robust Total Weight Selection: Prefer Document-Level Totals if non-zero
    inv_doc_total = clean_num(invoice_data.get("total_gross_weight_kg") or invoice_data.get("total_weight"))
    bol_doc_total = clean_num(bol_data.get("total_gross_weight_kg") or bol_data.get("total_weight"))
    
    inv_items_sum = sum(get_w(item) for item in invoice_items)
    bol_items_sum = sum(get_w(item) for item in bol_items)
    
    # Selection Logic: Document Total > Items Sum
    inv_total_weight = inv_doc_total if inv_doc_total > 0 else inv_items_sum
    bol_total_weight = bol_doc_total if bol_doc_total > 0 else bol_items_sum

    audit_results = []

    # SCENARIO A: Many-to-One or One-to-Many Consolidation
    if (len(invoice_items) > 1 and len(bol_items) == 1) or (len(bol_items) > 1 and len(invoice_items) == 1):
        weight_delta = abs(inv_total_weight - bol_total_weight)
        
        status = "COMPLIANT"
        if inv_total_weight == 0 or bol_total_weight == 0:
            status = "DATA_INCOMPLETE"
        elif weight_delta > (inv_total_weight * weight_tolerance + 1e-6):
            status = "DISCREPANCY_DETECTED"
            
        audit_results.append({
            "invoice_item": f"AGGREGATE MANIFEST ({len(invoice_items)} Items)",
            "bol_item": f"CONSOLIDATED SHIPMENT ({len(bol_items)} Items)",
            "quantity_inv": sum(int(clean_num(i.get('quantity') or i.get('qty'))) for i in invoice_items),
            "quantity_bol": sum(int(clean_num(i.get('quantity') or i.get('qty'))) for i in bol_items),
            "gross_weight_inv": round(inv_total_weight, 2),
            "gross_weight_bol": round(bol_total_weight, 2),
            "net_weight_inv": round(sum(clean_num(i.get('net_weight_kg') or i.get('net_kg')) for i in invoice_items), 2),
            "net_weight_bol": round(sum(clean_num(i.get('net_weight_kg') or i.get('net_kg')) for i in bol_items), 2),
            "weight_delta_kg": round(weight_delta, 2),
            "variance_pct": round((weight_delta / inv_total_weight * 100), 2) if inv_total_weight > 0 else 0,
            "status": status
        })

    # SCENARIO B: Standard N-to-N Matching
    elif invoice_items and bol_items:
        num_inv = len(invoice_items)
        num_bol = len(bol_items)
        cost_matrix = np.zeros((num_inv, num_bol))

        has_item_weights = False
        for i, inv in enumerate(invoice_items):
            inv_w = get_w(inv)
            if inv_w > 0: has_item_weights = True
            for j, bol in enumerate(bol_items):
                bol_w = get_w(bol)
                cost_matrix[i, j] = abs(inv_w - bol_w)

        if has_item_weights:
            row_ind, col_ind = linear_sum_assignment(cost_matrix)
            for r, c in zip(row_ind, col_ind):
                inv_item = invoice_items[r]
                bol_item = bol_items[c]
                
                inv_gw = get_w(inv_item)
                bol_gw = get_w(bol_item)
                inv_qty = int(clean_num(inv_item.get('quantity') or inv_item.get('qty')))
                bol_qty = int(clean_num(bol_item.get('quantity') or bol_item.get('qty')))

                weight_delta = abs(inv_gw - bol_gw)
                qty_delta = abs(inv_qty - bol_qty)
                
                status = "COMPLIANT"
                if inv_gw == 0 or bol_gw == 0:
                    status = "DATA_INCOMPLETE"
                elif weight_delta > (inv_gw * weight_tolerance + 1e-6):
                    status = "DISCREPANCY_DETECTED"
                elif qty_delta > 0:
                    status = "DISCREPANCY_DETECTED"
                    
                audit_results.append({
                    "invoice_item": inv_item.get('name', 'Unknown'),
                    "bol_item": bol_item.get('name', 'Unknown'),
                    "quantity_inv": inv_qty,
                    "quantity_bol": bol_qty,
                    "gross_weight_inv": inv_gw,
                    "gross_weight_bol": bol_gw,
                    "net_weight_inv": clean_num(inv_item.get('net_weight_kg') or inv_item.get('net_kg')),
                    "net_weight_bol": clean_num(bol_item.get('net_weight_kg') or bol_item.get('net_kg')),
                    "weight_delta_kg": round(weight_delta, 2),
                    "variance_pct": round((weight_delta / inv_gw * 100), 2) if inv_gw > 0 else 0,
                    "status": status
                })

    # SCENARIO C: Global Fallback
    if not audit_results and (inv_total_weight > 0 or bol_total_weight > 0):
        weight_delta = abs(inv_total_weight - bol_total_weight)
        status = "COMPLIANT"
        if inv_total_weight == 0 or bol_total_weight == 0:
            status = "DATA_INCOMPLETE"
        elif weight_delta > (inv_total_weight * weight_tolerance + 1e-6):
            status = "DISCREPANCY_DETECTED"
            
        audit_results.append({
            "invoice_item": "TOTAL MANIFEST SHIPMENT",
            "bol_item": "TOTAL BILL OF LADING",
            "quantity_inv": 0,
            "quantity_bol": 0,
            "gross_weight_inv": round(inv_total_weight, 2),
            "gross_weight_bol": round(bol_total_weight, 2),
            "net_weight_inv": 0,
            "net_weight_bol": 0,
            "weight_delta_kg": round(weight_delta, 2),
            "variance_pct": round((weight_delta / inv_total_weight * 100), 2) if inv_total_weight > 0 else 0,
            "status": status
        })
        
    return audit_results
