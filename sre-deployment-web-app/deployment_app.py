import streamlit as st

# ✅ List of valid clients (all stored in lowercase for case-insensitive check)
VALID_CLIENTS = [
    "nhp", "avmed", "bcbsks", "bcbsla", "bcbsma", "bcbsnc", "bcbsri", "bcbssc", "bcbst", "bcbsvt",
    "bcid", "bluekc", "brighton", "carefirst", "centene", "cobaltblue", "tpa", "ers", "fallon",
    "hcsc", "hcslabor", "healthcomp", "highmark", "hmsa", "horizon", "kpwa", "kpco", "kpga",
    "kpnw", "lifewise", "medxoom", "moda", "molina", "firstchoice", "pai", "personify", "premera",
    "sandbox", "selecthealth", "sharedhealthms", "texicare", "triples", "trs"
]

st.set_page_config(page_title="Deployment Automation", layout="wide")

st.title("🚀 Deployment Automation")

# --- Inputs ---
client_input = st.text_input("Enter Client Name").strip().lower()
version = st.text_input("Enter Version (e.g., v25.3.1)").strip()
variant = st.selectbox("Select Deployment Variant", ["blue", "green"])

# --- Client validation ---
if client_input and client_input not in VALID_CLIENTS:
    st.error("⚠️ Invalid client. Please enter a valid client from the predefined list.")
    st.stop()

if client_input and version and variant:
    # Format client name for display (uppercase)
    client = client_input.upper()

    # Opposite variant for freeze
    opposite_variant = "green" if variant == "blue" else "blue"

    st.subheader("📋 Deployment Steps")

    # One day before deployment info
    st.markdown("### One Day Before Deployment Scale out Steps")
    steps_before = [
        f"Freeze Passive → `dradis freeze {client} production_{opposite_variant}`",
        f"Snapshot → `dradis snapshot {client} production_{opposite_variant}`",
        f"Scaleout → `dradis make {client} production_{opposite_variant} ready for cutover`",
        f"Handover to QA → Passive production_{opposite_variant} is QA ready. Please validate"
    ]
    for idx, step in enumerate(steps_before, start=1):
        st.write(f"**{idx}.** {step}")

    # Cutover steps
    st.markdown("### Cutover Steps")
    steps_cutover = [
        f"Swap variants → `dradis make variant {variant} active for {client} production`",
        f"Clear cache → `dradis clear cache for api {client} production_{variant}`\n\n"
        f"`dradis clear cache for etl {client} production_{variant}`\n\n"
        f"`dradis clear cost for {client} production_{variant}`",
        "Final Handover → see below message"
    ]
    for idx, step in enumerate(steps_cutover, start=1):
        st.write(f"**{idx}.** {step}")

    # Final multi-line cutover message
    st.markdown(
        """
        ---
        ✅ **Cutover Completion Message:**

        The cutover process is now complete, and S365 caches have been cleared.  
        Please proceed with validation.  
        Kindly allow a few more minutes for any residual errors to settle down.  
        Let us know if you notice any issues.  

        Thanks 🙏
        """
    )

    # Validation endpoints
    st.subheader("🔗 Validation Endpoints")
    st.markdown(f"- [Health Check](https://app-ops.aws.mdx.med/deploys?client={client}&env=production&variant={variant})")
    st.markdown(f"- [Index Status](https://data-prd-{variant}-{client.lower()}.aws.mdx.med/index_status)")
    st.markdown(f"- [Reference Batch](https://solr-master-prd-{variant}-{client.lower()}.aws.mdx.med:8443/solr/reference/select?fq=type%3A%22PlatformSearch%3A%3ADocuments%3A%3AReferenceBatchMeta%22&q=*%3A*&sort=batch_created_at_ds+desc)")
    st.markdown(f"- [Billing Codes](https://solr-cost-prd-{variant}-{client.lower()}.aws.mdx.med:8443/solr/cost/select?fq=type%3A%22PlatformSearch%3A%3ADocuments%3A%3ABillingCode%22&q=*%3A*&sort=batch_created_at_ds+desc)")
    st.markdown(f"- [Replication Status](https://data-prd-{variant}-{client.lower()}.aws.mdx.med/replication_status)")