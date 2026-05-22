import os
import json

def extract_structured_invoice(raw_input_text: str) -> dict:
    """
    Parses incoming raw logistics metadata strings into highly typed dictionary formats.
    Operates completely locally via a clean JSON fallback if API configurations are empty.
    """
    # Check if we should try hitting an online LLM processor (Gemini)
    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                config={'response_mime_type': 'application/json'},
                contents=f"You are a logistics structural parsing agent. Extract the following logistics data into a strict JSON object with 'invoice_number', 'supplier', 'total_gross_weight_kg', and an 'items' list where each item has 'name', 'hs_code', 'quantity', 'gross_weight_kg', 'net_weight_kg', 'total_value_usd', and 'context_tags'. IMPORTANT: All numeric values MUST be pure floats/ints. Remove all commas, 'KGS', 'KG', '$', or spaces from numbers. Example: '$1,420.00' must be returned as 1420.00.\n\n{raw_input_text}"
            )

            return json.loads(response.text)
        except Exception:
            # Drop silently into local regex/JSON block if endpoint times out or drops
            pass

    # Safe Local Extraction Fallback Strategy
    try:
        return json.loads(raw_input_text)
    except Exception:
        return {
            "invoice_number": "ERR-UNKNOWN",
            "supplier": "MALFORMED_PAYLOAD_NODE",
            "items": []
        }


def extract_from_pdf(pdf_bytes: bytes) -> dict:
    """
    Uses Gemini's multimodal capabilities to extract structured logistics data 
    from a multipage PDF document.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "API Key missing for PDF processing."}

    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)

        # Construct a strict multimodal prompt to prioritize global weight declarations
        prompt = (
            "You are a logistics document analyst. Analyze this PDF document. "
            "Identify the Commercial Invoice and the Bill of Lading. "
            "1. GLOBAL WEIGHTS: Search for 'Gross Weight' and 'Net Weight' for the entire document. "
            "2. ITEMS: Extract unique line items. Capture 'hs_code' and 'total_value_usd' for each item. Do NOT include 'TOTAL' rows in 'items'. "
            "3. DATA INTEGRITY: Extract the EXACT numbers and codes. Do NOT normalize or correct them. "
            "4. FORMATTING: All numeric values (weights, qty, values) MUST be pure floats/ints. NEVER include commas, spaces, or currency symbols. "
            "\n\nExtract the data into a single JSON object: \n"
            "{ \"invoice\": { \"invoice_number\": \"...\", \"total_gross_weight_kg\": 0.0, \"items\": [{\"name\": \"...\", \"hs_code\": \"...\", \"quantity\": 0, \"gross_weight_kg\": 0.0, \"net_weight_kg\": 0.0, \"total_value_usd\": 0.0}] }, "
            "  \"bol\": { \"bol_number\": \"...\", \"total_gross_weight_kg\": 0.0, \"items\": [{\"name\": \"...\", \"hs_code\": \"...\", \"quantity\": 0, \"gross_weight_kg\": 0.0, \"net_weight_kg\": 0.0, \"total_value_usd\": 0.0}] } }\n\n"
            "IMPORTANT: Return ONLY the JSON object."
        )



        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config={'response_mime_type': 'application/json'},
            contents=[
                prompt,
                types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
            ]
        )

        return json.loads(response.text)
    except Exception as e:
        return {"error": f"PDF Extraction Failed: {str(e)}"}


def analyze_discrepancies(audit_results: list, sanitized_invoice: dict) -> str:
    """
    Evaluates physical layout anomalies flag logs compiled by the match engine, 
    spinning up risk explanations for operator analysis.
    """
    supplier = sanitized_invoice.get("supplier", "Unknown Supplier")

    if not audit_results:
        return "### ⚡ System Status Report\n\nAll weight checks matched within structural constraints. No tactical risk vectors flagged for this inbound manifest block."

    discrepancies = [res for res in audit_results if res.get("status") == "DISCREPANCY_DETECTED"]

    if not discrepancies:
        return "### ⚡ System Status Report\n\nAll items matched across documents within tolerances. No anomalies detected."

    # Attempt edge-context enrichment online if configured (Gemini)
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)

            prompt = f"Analyze these logistics variations found for supplier '{supplier}': {json.dumps(discrepancies)}"
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"You are an expert logistics risk and anomaly analysis terminal. Provide actionable threat explanations regarding these weight deviations: {prompt}"
            )
            return response.text
        except Exception:
            pass
    # Bulletproof Offline Structural Report Generation
    report = f"### ⚠️ Local Threat & Anomaly Assessment\n\n"
    report += f"**Operational Node Audit:** Local parsing verified anomalies with **{supplier}**.\n\n"
    report += "#### Identified Structural Concerns:\n"

    for issue in discrepancies:
        name = issue.get("invoice_item", "Unknown Item")
        delta = issue.get("weight_delta_kg", 0.0)
        report += f"- **{name}**: Weight delta of **{delta} kg** detected between documents.\n"

    report += "\n\n*Directives: Check cargo density, moisture absorption metrics, or verify packaging configurations.*"
    return report