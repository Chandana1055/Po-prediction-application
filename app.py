import json
import time
import streamlit as st
from classifier import classify_po, MODEL

st.set_page_config(page_title="PO L1-L2-L3 Classifier", layout="centered")

st.title("PO L1-L2-L3 Classifier")
st.caption("Classify purchase order descriptions using the enterprise taxonomy.")

show_raw_output = st.sidebar.checkbox("Show raw model output", value=True)

if "po_description" not in st.session_state:
    st.session_state["po_description"] = ""
if "supplier" not in st.session_state:
    st.session_state["supplier"] = ""

with st.form("classifier_form"):
    po_description = st.text_area(
        "PO Description",
        height=140,
        placeholder="Example: DocuSign Inc - eSignature Enterprise Pro Subscription",
        help="Enter the full PO line item description.",
        key="po_description",
    )
    supplier = st.text_input(
        "Supplier (optional)",
        placeholder="Example: DocuSign Inc",
        help="Leave blank if the supplier is unknown.",
        key="supplier",
    )
    submit = st.form_submit_button(
        "Classify",
        disabled=not po_description.strip(),
    )

col_left, col_right = st.columns([1, 3])
with col_left:
    clear = st.button("Clear", type="secondary")

if clear:
    st.session_state["po_description"] = ""
    st.session_state["supplier"] = ""
    st.rerun()

if submit:
    if not po_description.strip():
        st.warning("Please enter a PO description.")
    else:
        start = time.perf_counter()
        try:
            with st.spinner("Classifying..."):
                result = classify_po(po_description, supplier)
            elapsed = time.perf_counter() - start
        except Exception as exc:
            st.error("Classification failed. Please check your API key or try again.")
            st.caption(f"Error details: {exc}")
        else:
            st.subheader("Classification Result")
            st.caption(f"Model: {MODEL} · Latency: {elapsed:.2f}s")

            try:
                parsed = json.loads(result)
            except Exception:
                st.warning("Model returned invalid JSON.")
                with st.expander("Raw response", expanded=True):
                    st.text(result)
            else:
                st.json(parsed)
                if show_raw_output:
                    with st.expander("Raw response"):
                        st.text(result)
