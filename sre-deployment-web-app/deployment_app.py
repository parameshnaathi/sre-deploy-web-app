import streamlit as st

# Valid client list (all stored as lowercase for easier matching)
VALID_CLIENTS = [
    "nhp", "avmed", "bcbsks", "bcbsla", "bcbsma", "bcbsnc", "bcbsri", "bcbssc",
    "bcbst", "bcbsvt", "bcid", "bluekc", "brighton", "carefirst", "centene",
    "cobaltblue", "tpa", "ers", "fallon", "hcsc", "hcslabor", "healthcomp",
    "highmark", "hmsa", "horizon", "kpwa", "kpco", "kpga", "kpnw", "lifewise",
    "medxoom", "moda", "molina", "firstchoice", "pai", "personify", "premera",
    "sandbox", "selecthealth", "sharedhealthms", "texicare", "triples", "trs"
]

st.set_page_config(page_title="Dradis Deployment Automation", page_icon="🚀", layout="centered")

st.title("🚀 Dradis Deployment Automation")
st.write(
    """
    This tool generates **deployment steps** for a client environment.  
    **Constraint**: First freeze is always on the opposite variant.  

    Commands are in **copyable code snippets**, with clickable validation endpoints below each.
    """
)

# Inputs
client = st.text_input("Client Name")
version = st.text_input("Version (e.g., 1.2.3)")
variant = st.text_input("Deployment Variant (a/b)").lower()

if st.button("Generate Deployment Steps"):
    client_normalized = client.strip().lower()

    if client_normalized not in VALID_CLIENTS:
        st.error("❌ Invalid client name. Please enter a valid client.")
    elif variant not in ["a", "b"]:
        st.error("❌ Deployment variant must be either 'a' or 'b'.")
    else:
        # Ensure lowercase client is always used in commands
        client_display = client_normalized  
        opposite_variant = "b" if variant == "a" else "a"

        st.subheader("1. Freeze Active")
        st.code(f"dradis freeze {client_display} production_{opposite_variant}", language="bash")

        st.subheader("2. Deploy All Things")
        st.code(f"dradis deploy all the things {version} to {client_display} production_{variant}", language="bash")

        st.subheader("3. Snapshot")
        st.code(f"dradis snapshot {client_display} production_{variant}", language="bash")

        st.subheader("4. Scaleout")
        st.code(f"dradis scaleout {client_display} production_{variant}", language="bash")

        st.subheader("5. Handover to QA")
        st.write("Deployment has been completed. Please proceed with QA validation.")

        st.subheader("6. Swap Variants")
        st.code(f"dradis swap {client_display} production_{variant}", language="bash")

        st.subheader("7. Clear Cache")
        st.code(f"dradis clear cache {client_display}", language="bash")

        st.subheader("8. Final Handover")
        st.write(
            """The cutover process is now complete, and S365 caches have been cleared.  
            Please proceed with validation.  
            Kindly allow a few more minutes for any residual errors to settle down.  
            Let us know if you notice any issues.  
            Thanks"""
        )

        # Validation Endpoints
        st.subheader("🔗 Validation Endpoints")
        st.markdown(f"[Health Check](https://{client_display}.example.com/health)", unsafe_allow_html=True)
        st.markdown(f"[API Status](https://{client_display}.example.com/status)", unsafe_allow_html=True)
        st.markdown(f"[Login Page](https://{client_display}.example.com/login)", unsafe_allow_html=True)