# app.py
import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

# Absolute imports from your local engine subdirectory
from engine.ai_agents import extract_structured_invoice, analyze_discrepancies, extract_from_pdf
from engine.match_engine import audit_shipment_graph
from engine.trie_engine import autocomplete_search_tags, validate_hs_code

# Load environment variables
load_dotenv()

# =====================================================================
# SYSTEM INITIALIZATION & SOPHISTICATED THEMING
# =====================================================================
st.set_page_config(
    page_title="MMLogicInt Terminal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deep Inject UI Custom Styling for an Industrial/Technical Dashboard Feeling
st.markdown("""
    <style>
        .stApp {
            background-color: #0E1117;
            color: #E2E8F0;
            font-family: 'SF Mono', 'Roboto Mono', Menlo, Monaco, Consolas, monospace;
        }
        section[data-testid="stSidebar"] {
            background-color: #1A1F2C !important;
            border-right: 1px solid #2D3748;
        }
        .metric-card {
            background-color: #1A1F2C;
            border: 1px solid #2D3748;
            border-radius: 6px;
            padding: 18px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }
        .anomaly-card {
            background: linear-gradient(90deg, rgba(239,68,68,0.15) 0%, rgba(26,31,44,1) 100%);
            border-left: 4px solid #EF4444;
            border-top: 1px solid #2D3748;
            border-right: 1px solid #2D3748;
            border-bottom: 1px solid #2D3748;
            padding: 15px;
            border-radius: 0 6px 6px 0;
            margin-bottom: 12px;
        }
        .clear-card {
            background: linear-gradient(90deg, rgba(16,185,129,0.15) 0%, rgba(26,31,44,1) 100%);
            border-left: 4px solid #10B981;
            border-top: 1px solid #2D3748;
            border-right: 1px solid #2D3748;
            border-bottom: 1px solid #2D3748;
            padding: 15px;
            border-radius: 0 6px 6px 0;
        }
        .tech-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #718096;
            margin-bottom: 4px;
        }
        .tech-value {
            font-size: 1.4rem;
            font-weight: 700;
            color: #F7FAFC;
        }
    </style>
""", unsafe_allow_html=True)

# Main Banner Core Terminal Branding
st.markdown("""
    <div style="background-color:#1A1F2C; padding:20px; border-radius:6px; margin-bottom:25px; border: 1px solid #2D3748; border-left: 4px solid #00FF66;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="color:#ffffff; margin:0; font-family:monospace; font-size:1.75rem; font-weight:700; letter-spacing:-0.5px;">🛡️ MMLogicInt // SYSTEMS</h1>
                <p style="color:#4A5568; margin:3px 0 0 0; font-family:monospace; font-size:0.75rem; text-transform:uppercase; letter-spacing:1.5px;">
                    Multimodal Manifest Logic Integration // Edge AI
                </p>
            </div>
            <div style="text-align: right; font-family: monospace; font-size: 0.75rem; color: #718096;">
                SYS_STATUS: ACTIVE<br>
                LOC_NODE: CORE_EDGE_01
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# System status reporting inside sidebar
with st.sidebar:
    st.markdown("<div style='padding-top:10px;'></div>", unsafe_allow_html=True)
    st.markdown("### 🎛️ CORE METADATA")
    st.divider()
    
    # Destination Region Selector for Financial Audit
    st.markdown("### 🌍 DESTINATION HUB")
    dest_region = st.selectbox("Select Target Region", options=["Canada (CA)", "USA (US)", "Europe (EU)"], index=0)
    region_code = dest_region.split("(")[1].replace(")", "")
    
    st.divider()
    
    api_key_exists = bool(os.getenv("GEMINI_API_KEY"))
    if api_key_exists:
        st.markdown("""
            <div style="background-color:rgba(16,185,129,0.1); border: 1px solid #10B981; padding:10px; border-radius:4px; text-align:center; font-size:0.8rem; color:#10B981; font-weight:bold;">
                ● GEMINI TRANSCEIVER ONLINE
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="background-color:rgba(245,158,11,0.1); border: 1px solid #F59E0B; padding:10px; border-radius:4px; text-align:center; font-size:0.8rem; color:#F59E0B; font-weight:bold;">
                ⬢ LOCAL CORE ISOLATION MODE
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)
    st.markdown("### ⚡ ENGINE SUBSYSTEMS")
    st.markdown("""
        <div style="font-size:0.8rem; color:#A0AEC0; line-height:1.6;">
            <code style="color:#00FF66;">trie_engine</code> ➔ Substring Token Isolation<br>
            <code style="color:#00FF66;">match_engine</code> ➔ Graph Mass Audit<br>
            <code style="color:#00FF66;">ai_agent</code> ➔ Context Anomaly Parser
        </div>
    """, unsafe_allow_html=True)

# =====================================================================
# WORKSPACE LAYOUT: SIDE-BY-SIDE CONTROL SPLIT
# =====================================================================
# PDF Extraction Layer
st.markdown("### 📄 MULTIMODAL PDF INGESTION LAYER")
pdf_file = st.file_uploader("Upload Multi-page Logistics PDF (Invoice + BOL)", type=["pdf"])

if pdf_file:
    if st.button("🚀 EXTRACT DATA FROM PDF", use_container_width=True):
        with st.spinner("Gemini 2.0 Flash is analyzing document visual structures..."):
            extracted_data = extract_from_pdf(pdf_file.read())
            if "error" in extracted_data:
                st.error(extracted_data["error"])
            else:
                st.session_state["invoice_json"] = json.dumps(extracted_data.get("invoice", {}), indent=2)
                st.session_state["bol_json"] = json.dumps(extracted_data.get("bol", {}), indent=2)
                st.success("Documents identified and extracted successfully!")

st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

col_left_panel, col_right_panel = st.columns([1, 1], gap="large")

with col_left_panel:
    st.markdown("### 📥 DATA INGESTION ENGINE")
    
    raw_invoice_input = st.text_area(
        "Commercial Invoice Ingest (JSON / String)",
        value=st.session_state.get("invoice_json", ""),
        height=250,
        placeholder="Paste Invoice JSON here or extract from PDF above..."
    )

    raw_bol_input = st.text_area(
        "Bill of Lading Ingest (JSON / String)",
        value=st.session_state.get("bol_json", ""),
        height=250,
        placeholder="Paste BOL JSON here or extract from PDF above..."
    )

with col_right_panel:
    st.markdown("### 🎚️ PARAMETER DEVIATION TUNING")
    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
    weight_tolerance = st.slider("Graph Discrepancy Tolerance Max (%)", min_value=0.0, max_value=10.0, value=2.5, step=0.5)
    
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    auto_tag = st.checkbox("Cross-reference Token Streams via Trie Index", value=True)
    
    st.markdown(f"""
        <div style="background-color:#1A1F2C; border: 1px solid #2D3748; padding:15px; border-radius:6px; margin-top:25px; font-size:0.85rem; color:#718096; line-height:1.5;">
            <strong style="color:#E2E8F0;">Operational Ruleset:</strong><br>
            Altering the sliding threshold configuration directly dictates the sensitivity matrix of our mass distribution analysis engine. Current limit is set to flag anomalies scaling past <strong>{weight_tolerance}%</strong> deviation from physical baseline logs.
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

col_btn, _ = st.columns([1, 2])
with col_btn:
    execute_pipeline = st.button("RUN TACTICAL PIPELINE ANALYSIS", type="primary", use_container_width=True)

# =====================================================================
# RUNTIME LOGIC & TELEMETRY OUTPUTS
# =====================================================================
if execute_pipeline:
    st.markdown("<br><hr style='border-color:#2D3748;'><br>", unsafe_allow_html=True)
    st.markdown("### 📊 REAL-TIME CORE TELEMETRY OUTPUTS")
    
    with st.spinner("Processing system arrays through localized node modules..."):
        try:
            # 1. Extraction phase
            structured_invoice = extract_structured_invoice(raw_invoice_input)
            structured_bol = extract_structured_invoice(raw_bol_input) # Reusing agent for BOL parsing
            
            # 2. Sanitization & Trie Enrichment
            def clean_numeric(value):
                if value is None: return 0.0
                if isinstance(value, (int, float)): return float(value)
                try:
                    import re
                    # Extract only numbers and the first decimal point found
                    nums_only = re.findall(r"[-+]?\d*\.\d+|\d+", str(value).replace(',', ''))
                    return float(nums_only[0]) if nums_only else 0.0
                except (ValueError, TypeError, IndexError):
                    return 0.0

            def sanitize_items(raw_items):
                sanitized_list = []
                for item in raw_items:
                    raw_gw = item.get("gross_weight_kg") or item.get("weight_kg") or item.get("weight") or 0.0
                    raw_nw = item.get("net_weight_kg") or 0.0
                    raw_qty = item.get("quantity") or item.get("qty") or 0
                    raw_hs = str(item.get("hs_code") or "").strip()
                    raw_val = item.get("total_value_usd") or item.get("value") or 0.0
                    
                    clean_gw = clean_numeric(raw_gw)
                    clean_nw = clean_numeric(raw_nw)
                    clean_val = clean_numeric(raw_val)
                    try:
                        clean_qty = int(float(str(raw_qty).replace(',', '').strip()))
                    except:
                        clean_qty = 0
                    
                    # VALIDATE HS CODE against the Local Trie Database
                    hs_validation = validate_hs_code(raw_hs) if raw_hs else {"valid": False, "description": "No Code Provided", "rates": {}}
                    hs_status = "✅ Valid" if hs_validation.get("valid") else "⚠️ Unindexed"
                    
                    # Calculate Projected Duty
                    rates = hs_validation.get("rates", {"CA": 0.0, "US": 0.0, "EU": 0.0})
                    duty_rate = rates.get(region_code, 0.0)
                    projected_duty = clean_val * duty_rate

                    raw_tags = item.get("context_tags") or item.get("tags") or []
                    if auto_tag and raw_tags:
                        try:
                            processed_tags = autocomplete_search_tags(raw_tags if isinstance(raw_tags, list) else [str(raw_tags)])
                        except Exception:
                            processed_tags = raw_tags
                    else:
                        processed_tags = raw_tags
                    
                    sanitized_list.append({
                        "name": str(item.get("name", "Unknown Item")),
                        "qty": clean_qty,
                        "hs_code": f"{raw_hs} ({hs_status})",
                        "value_usd": clean_val,
                        "projected_duty": projected_duty,
                        "gross_kg": clean_gw,
                        "net_kg": clean_nw,
                        "tags": ", ".join([str(t).lower() for t in processed_tags]) if isinstance(processed_tags, list) else str(processed_tags)
                    })
                return sanitized_list

            adapted_invoice_items = sanitize_items(structured_invoice.get("items", []))
            adapted_bol_items = sanitize_items(structured_bol.get("items", []))

            sanitized_invoice = {
                "invoice_number": str(structured_invoice.get("invoice_number", "UNKNOWN")),
                "supplier": str(structured_invoice.get("supplier", "UNKNOWN")),
                "total_gross_weight_kg": clean_numeric(structured_invoice.get("total_gross_weight_kg")),
                "items": adapted_invoice_items
            }
            
            sanitized_bol = {
                "bol_number": str(structured_bol.get("bol_number", "UNKNOWN")),
                "total_gross_weight_kg": clean_numeric(structured_bol.get("total_gross_weight_kg")),
                "items": adapted_bol_items
            }

            # DEBUG: Display raw extraction weights for transparency
            with st.expander("🛠️ DEBUG: RAW WEIGHT EXTRACTION LOGS"):
                st.markdown("### 📊 Document Totals (Parsed)")
                st.write(f"**Invoice Total:** {sanitized_invoice['total_gross_weight_kg']} kg")
                st.write(f"**BOL Total:** {sanitized_bol['total_gross_weight_kg']} kg")
                st.markdown("---")
                st.markdown("### 📦 Raw AI Extraction (Unfiltered)")
                st.json({"raw_invoice": structured_invoice, "raw_bol": structured_bol})

            # =====================================================================
            # ADAPTIVE GRAPH ALIGNMENT CAPTURE
            # =====================================================================
            tolerance_ratio = float(weight_tolerance) / 100.0

            # Execute graph routing alignment check - PASS SYMMETRIC DICTS
            audit_results = audit_shipment_graph(
                sanitized_invoice,
                sanitized_bol,
                weight_tolerance=tolerance_ratio
            )

            ai_insights = analyze_discrepancies(audit_results, sanitized_invoice)
            
            discrepancy_count = len([res for res in audit_results if res.get("status") == "DISCREPANCY_DETECTED"])

            # Render Metric Layout Cards
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            
            with m_col1:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="tech-label">MANIFEST ID REFERENCE</div>
                        <div class="tech-value" style="color:#00FF66;">{sanitized_invoice["invoice_number"]}</div>
                    </div>
                """, unsafe_allow_html=True)
                
            with m_col2:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="tech-label">ROUTING ORIGIN SHIELD</div>
                        <div class="tech-value">{sanitized_invoice["supplier"]}</div>
                    </div>
                """, unsafe_allow_html=True)
                
            with m_col3:
                if discrepancy_count > 0:
                    st.markdown(f"""
                        <div class="metric-card" style="border: 1px solid #EF4444;">
                            <div class="tech-label" style="color:#EF4444;">ANOMALIES INTERCEPTED</div>
                            <div class="tech-value" style="color:#EF4444;">{discrepancy_count} CRITICAL</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div class="metric-card" style="border: 1px solid #10B981;">
                            <div class="tech-label" style="color:#10B981;">SECURITY SANITIZATION</div>
                            <div class="tech-value" style="color:#10B981;">CLEAR PASS</div>
                        </div>
                    """, unsafe_allow_html=True)

            with m_col4:
                total_duty = sum(i.get("projected_duty", 0.0) for i in adapted_invoice_items)
                st.markdown(f"""
                    <div class="metric-card" style="border: 1px solid #00FF66;">
                        <div class="tech-label">EST. TAX LIABILITY ({region_code})</div>
                        <div class="tech-value" style="color:#00FF66;">${total_duty:,.2f}</div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

            # =====================================================================
            # LIVE SYSTEM AUDIT LOG (Visual Simulation for Demo)
            # =====================================================================
            st.markdown("#### 📡 LIVE CROSS-DOCUMENT RECONCILIATION LOG")
            log_container = st.empty()
            audit_log_text = ""
            
            # Simulate a live processing feel for the video demo
            import time
            for res in audit_results:
                status_icon = "🟢 [OK]" if res.get("status") == "COMPLIANT" else "🔴 [ALERT]"
                item_name = res.get("invoice_item")
                log_entry = f"{status_icon} Analyzing {item_name}... Alignment Check: {res.get('status')}\n"
                audit_log_text += log_entry
                log_container.code(audit_log_text)
                time.sleep(0.4) # Small delay for "live" feel in video

            st.markdown("<div style='margin-top:30px;'></div>", unsafe_allow_html=True)

            # Two-Column Technical Visualization Breakdown
            col_v1, col_v2 = st.columns([1, 1], gap="large")

            with col_v1:
                st.markdown("#### ⚖️ AUDIT RECONCILIATION MATRIX")
                st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                
                # RECONCILIATION TABLE: Side-by-Side Comparison
                audit_df_data = []
                for res in audit_results:
                    audit_df_data.append({
                        "Match Status": "✅" if res.get("status") == "COMPLIANT" else "❌",
                        "Item (Invoice)": res.get("invoice_item"),
                        "Item (BOL)": res.get("bol_item"),
                        "Qty (I/B)": f"{res.get('quantity_inv')} / {res.get('quantity_bol')}",
                        "Gross (I/B)": f"{res.get('gross_weight_inv')} / {res.get('gross_weight_bol')}",
                        "Delta (%)": f"{res.get('variance_pct')}%"
                    })
                
                df_audit = pd.DataFrame(audit_df_data)
                if not df_audit.empty:
                    st.dataframe(
                        df_audit,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.caption("No valid matching logs generated.")
                
                st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
                st.markdown("#### 📄 INBOUND MANIFEST SPEC")
                
                df_raw = pd.DataFrame(adapted_invoice_items)
                if not df_raw.empty:
                    st.dataframe(
                        df_raw,
                        column_config={
                            "name": "Component Spec",
                            "qty": "Qty",
                            "hs_code": "Regulatory HS Code",
                            "value_usd": "Value (USD)",
                            "projected_duty": "Est. Duty ($)",
                            "gross_kg": "Gross",
                            "net_kg": "Net",
                            "tags": "Trie Tokens"
                        },
                        use_container_width=True,
                        hide_index=True
                    )

            with col_v2:
                st.markdown("#### 🧠 AI AGENT CONTEXT ENRICHMENT REPORT")
                st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div style="background-color:#1A1F2C; border: 1px solid #2D3748; padding:20px; border-radius:6px; font-size:0.9rem; line-height:1.6; color:#CBD5E1; box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);">
                        {str(ai_insights)}
                    </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error("### Fatal Internal System Error Exception")
            st.code(str(e), language="python")