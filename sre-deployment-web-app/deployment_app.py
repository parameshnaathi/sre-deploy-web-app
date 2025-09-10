# ...existing code...
import streamlit as st
from deployment_logic import (
    get_client_dropdown_options,
    get_display_to_canonical,
    generate_deployment_plan
)
from slack_utils import send_command_to_slack
from datetime import datetime
from pg_logging import log_command_to_postgres

# ---------------- Streamlit UI ----------------
st.title("🚀 Dradis Deployment Automation")
st.markdown("""
This tool generates **deployment steps** for a client environment.  
**Constraint:** First freeze is always on the opposite variant.  
Commands are in **copyable code snippets**, with **clickable validation endpoints** below each.
""")

# Client dropdown with search (case-insensitive)


# --- Session State Setup ---
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'selected_client_display' not in st.session_state:
    st.session_state.selected_client_display = None
if 'version' not in st.session_state:
    st.session_state.version = ''
if 'variant' not in st.session_state:
    st.session_state.variant = 'a'
if 'plan' not in st.session_state:
    st.session_state.plan = None
if 'slack_result' not in st.session_state:
    st.session_state.slack_result = {}

# --- User Login ---
st.header("User Login")
username = st.text_input("Enter your name or email to use the automation:", value=st.session_state.username, key="username_input")
st.session_state.username = username.strip()
if not st.session_state.username:
    st.warning("Please enter your name or email to use the automation.")
    st.stop()

CLIENT_DROPDOWN_OPTIONS = get_client_dropdown_options()
DISPLAY_TO_CANONICAL = get_display_to_canonical()

selected_client_display = st.selectbox(
    "Client Name",
    CLIENT_DROPDOWN_OPTIONS,
    index=0,
    key="client_dropdown",
    help="Start typing to search for a client (case-insensitive)"
)
st.session_state.selected_client_display = selected_client_display

version = st.text_input("Version (e.g., 1.2.3)", value=st.session_state.version, key="version_input").strip()
st.session_state.version = version

variant = st.selectbox("Deployment Variant", ["a", "b"], index=["a", "b"].index(st.session_state.variant) if st.session_state.variant in ["a", "b"] else 0, key="variant_select")
st.session_state.variant = variant

generate_clicked = st.button("Generate Deployment Steps")

if generate_clicked:
    if not selected_client_display or not version:
        st.warning("Please provide both client name and version.")
        st.session_state.plan = None
    else:
        canonical_client = DISPLAY_TO_CANONICAL.get(selected_client_display.upper())
        from config import VALID_CLIENTS
        if not canonical_client or canonical_client not in VALID_CLIENTS:
            st.error("⚠️ Invalid client. Please enter a valid client from the predefined list.")
            st.session_state.plan = None
        else:
            st.session_state.plan = generate_deployment_plan(canonical_client, version, variant)
            st.session_state.slack_result = {}  # Reset slack results

# --- Display Plan if available ---
plan = st.session_state.plan
if plan:
    step_counter = 1
    for idx, item in enumerate(plan):
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
            for cmd_idx, cmd in enumerate(item["commands"]):
                st.code(cmd, language='bash')
                button_key = f"send_slack_{idx}_{cmd_idx}"
                if st.button(f"Send to Slack", key=button_key):
                    try:
                        success = send_command_to_slack(cmd)
                        st.session_state.slack_result[button_key] = success
                        # Log the command execution to PostgreSQL
                        log_command_to_postgres(st.session_state.username, cmd)
                    except Exception as e:
                        st.session_state.slack_result[button_key] = str(e)
                # Show Slack result if available
                if button_key in st.session_state.slack_result:
                    result = st.session_state.slack_result[button_key]
                    if result is True:
                        st.success("Command sent to Slack #sre-bot-playground.")
                    elif result is False:
                        st.error("As of now this feature disbaled for security reasons.")
                    else:
                        st.error(f"Slack error: {result}")
            if "validation" in item:
                st.markdown(f"[Validation Endpoint]({item['validation']})", unsafe_allow_html=True)