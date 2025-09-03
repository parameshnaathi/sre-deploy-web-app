import streamlit as st

# ✅ Valid clients list (all lowercase for case-insensitive check)
VALID_CLIENTS = [
    "nhp", "avmed", "bcbsks", "bcbsla", "bcbsma", "bcbsnc", "bcbsri", "bcbssc", "bcbst", "bcbsvt",
    "bcid", "bluekc", "brighton", "carefirst", "centene", "cobaltblue", "tpa", "ers", "fallon",
    "hcsc", "hcslabor", "healthcomp", "highmark", "hmsa", "horizon", "kpwa", "kpco", "kpga",
    "kpnw", "lifewise", "medxoom", "moda", "molina", "firstchoice", "pai", "personify", "premera",
    "sandbox", "selecthealth", "sharedhealthms", "texicare", "triples", "trs"
]

def get_opposite_variant(variant: str) -> str:
    variant = variant.lower()
    if variant == "a":
        return "b"
    elif variant == "b":
        return "a"
    else:
        st.error("Variant must be 'a' or 'b'")
        return ""

def generate_deployment_plan(client: str, version: str, variant: str):
    opposite = get_opposite_variant(variant)
    if not opposite:
        return []
    plan = []

    # ---------------- Main Numbered Steps ----------------
    plan.append({"heading": "Freeze Active",
                 "commands": [f"dradis freeze {client} production_{opposite}"]})

    plan.append({"heading": "Deploy All Things",
                 "commands": [f"dradis deploy all the things {version} to {client} production_{variant}"],
                 "validation": f"https://app-ops.aws.mdx.med/deploys?client={client}&env=production&variant={variant}"})

    plan.append({"heading": "Full Indexing",
                 "commands": [f"dradis index data for {client} production_{variant}"],
                 "validation": f"https://data-prd-{variant}-{client.lower()}.aws.mdx.med/index_status"})

    plan.append({"heading": "Referencing",
                 "commands": [f"dradis index reference for {client} production_{variant}"],
                 "validation": f"https://solr-master-prd-{variant}-{client.lower()}.aws.mdx.med:8443/solr/reference/select?fq=type%3A%22PlatformSearch%3A%3ADocuments%3A%3AReferenceBatchMeta%22&q=*%3A*&sort=batch_created_at_ds+desc"})

    plan.append({"heading": "Billing Codes",
                 "commands": [f"dradis index billing_codes for {client} production_{variant}"],
                 "validation": f"https://solr-cost-prd-{variant}-{client.lower()}.aws.mdx.med:8443/solr/cost/select?fq=type%3A%22PlatformSearch%3A%3ADocuments%3A%3ABillingCode%22&q=*%3A*&sort=batch_created_at_ds+desc"})

    plan.append({"heading": "Solr: Replication",
                 "commands": [f"dradis cap solr:replicate for etl {client} production_{variant} debug"],
                 "validation": f"https://data-prd-{variant}-{client.lower()}.aws.mdx.med/replication_status"})

    # ---------------- One Day before Deployment Scale out Steps ----------------
    plan.append({"heading": "One Day before Deployment Scale out Steps", "numbered": False})

    plan.append({"heading": "Freeze Passive", "numbered": True,
                 "commands": [f"dradis freeze {client} production_{variant}"]})

    plan.append({"heading": "Snapshot", "numbered": True,
                 "commands": [f"dradis snapshot {client} production_{variant}"],
                 "validation": f"https://app-ops.aws.mdx.med/snapshots?env=production&client={client}&variant={variant}"})

    plan.append({"heading": "Scaleout", "numbered": True,
                 "commands": [f"dradis make {client} production_{variant} ready for cutover"],
                 "validation": f"https://app-ops.aws.mdx.med/client_environments?client={client}&env=production&variant={variant}"})

    plan.append({"heading": "Handover to QA", "numbered": True,
                 "commands": [f"Passive production_{variant} is QA ready. Please validate"]})

    # ---------------- Cutover Steps ----------------
    plan.append({"heading": "Cutover Steps", "numbered": False})

    plan.append({"heading": "Swap Variants", "numbered": True,
                 "commands": [f"dradis make variant {variant} active for {client} production"],
                 "validation": f"https://app-ops.aws.mdx.med/sidekiq/scheduled"})

    plan.append({"heading": "Clear Cache", "numbered": True,
                 "commands": [
                     f"dradis clear cache for api {client} production_{variant}",
                     f"dradis clear cache for etl {client} production_{variant}",
                     f"dradis clear cost for {client} production_{variant}"
                 ]})

    # Final Handover with multiline formatting
    final_handover_text = """The cutover process is now complete, and S365 caches have been cleared. Please proceed with validation. 
Kindly allow a few more minutes for any residual errors to settle down. Let us know if you notice any issues. 
Thanks"""
    plan.append({"heading": "Final Handover", "numbered": True,
                 "commands": [final_handover_text]})

    return plan

# ---------------- Streamlit UI ----------------
st.title("🚀 Dradis Deployment Automation")
st.markdown("""
This tool generates **deployment steps** for a client environment.  
**Constraint:** First freeze is always on the opposite variant.  
Commands are in **copyable code snippets**, with **clickable validation endpoints** below each.
""")

client_input = st.text_input("Client Name").strip()
version = st.text_input("Version (e.g., 1.2.3)").strip()
variant = st.selectbox("Deployment Variant", ["a", "b"])

if st.button("Generate Deployment Steps"):
    if not client_input or not version:
        st.warning("Please provide both client name and version.")
    else:
        client_lower = client_input.lower()
        if client_lower not in VALID_CLIENTS:
            st.error("⚠️ Invalid client. Please enter a valid client from the predefined list.")
        else:
            client = client_lower.upper()  # display uppercase for readability
            plan = generate_deployment_plan(client, version, variant)
            step_counter = 1
            for item in plan:
                numbered = item.get("numbered", True)
                # Display headings
                if "commands" not in item:
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