
import streamlit as st
from deployment_logic import (
    get_client_dropdown_options,
    get_display_to_canonical,
    generate_deployment_plan
)

# ---------------- Streamlit UI ----------------
st.title("🚀 Dradis Deployment Automation")
st.markdown("""
This tool generates **deployment steps** for a client environment.  
**Constraint:** First freeze is always on the opposite variant.  
Commands are in **copyable code snippets**, with **clickable validation endpoints** below each.
""")

# Client dropdown with search (case-insensitive)
CLIENT_DROPDOWN_OPTIONS = get_client_dropdown_options()
DISPLAY_TO_CANONICAL = get_display_to_canonical()
selected_client_display = st.selectbox(
    "Client Name",
    CLIENT_DROPDOWN_OPTIONS,
    index=0,
    key="client_dropdown",
    help="Start typing to search for a client (case-insensitive)"
)
version = st.text_input("Version (e.g., 1.2.3)").strip()
# 🔽 Variant is a dropdown (a/b)
variant = st.selectbox("Deployment Variant", ["a", "b"])

if st.button("Generate Deployment Steps"):
    if not selected_client_display or not version:
        st.warning("Please provide both client name and version.")
    else:
        # Map dropdown display name to canonical client name
        canonical_client = DISPLAY_TO_CANONICAL.get(selected_client_display.upper())
        from config import VALID_CLIENTS
        if not canonical_client or canonical_client not in VALID_CLIENTS:
            st.error("⚠️ Invalid client. Please enter a valid client from the predefined list.")
        else:
            plan = generate_deployment_plan(canonical_client, version, variant)
            step_counter = 1
            for item in plan:
                numbered = item.get("numbered", True)
                # Display headings
                if "commands" not in item:
                    # Heading without commands
                    if numbered:
                        st.subheader(f"{step_counter}. {item['heading']}")
                        step_counter += 1
                    else:
                        st.subheader(item['heading'])
                else:
                    if numbered:
                        st.subheader(f"{step_counter}. {item['heading']}")
                        step_counter += 1
                    else:
                        st.subheader(item['heading'])
                    for cmd in item["commands"]:
                        st.code(cmd, language='bash')
                    if "validation" in item:
                        st.markdown(f"[Validation Endpoint]({item['validation']})", unsafe_allow_html=True)