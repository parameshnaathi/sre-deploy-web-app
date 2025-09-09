# deployment_logic.py
from config import VALID_CLIENTS, CLIENT_ALIASES
import streamlit as st

# Build dropdown options: all valid clients and their aliases, capitalized, no duplicates
def get_client_dropdown_options():
    _dropdown_options_set = set(VALID_CLIENTS)
    _dropdown_options_set.update(CLIENT_ALIASES.keys())
    return sorted({name.upper() for name in _dropdown_options_set})

# Map dropdown display name (upper) to canonical client (lower)
def get_display_to_canonical():
    _dropdown_options_set = set(VALID_CLIENTS)
    _dropdown_options_set.update(CLIENT_ALIASES.keys())
    display_to_canonical = {}
    for name in _dropdown_options_set:
        canonical = CLIENT_ALIASES.get(name, name)
        display_to_canonical[name.upper()] = canonical
    return display_to_canonical

def get_opposite_variant(variant: str) -> str:
    variant = variant.lower()
    if variant == "a":
        return "b"
    elif variant == "b":
        return "a"
    else:
        st.error("Variant must be 'a' or 'b'")
        return ""

def generate_deployment_plan(client_lc: str, version: str, variant: str):
    """
    client_lc: client in lowercase (used for all commands/URLs)
    """

    # Map for validation endpoint client names
    VALIDATION_CLIENT_MAP = {
        "nhp": "allways",
        "tpa": "enterprise",
        "kpwa": "enterprise",
        "firstchoice": "myfch"
    }
    def get_validation_client_name(client_lc):
        return VALIDATION_CLIENT_MAP.get(client_lc, client_lc)

    opposite = get_opposite_variant(variant)
    if not opposite:
        return []
    plan = []

    # ---------------- Main Numbered Steps ----------------
    plan.append({"heading": "Freeze Active",
                 "commands": [f"dradis freeze {client_lc} production_{opposite}"]})

    plan.append({"heading": "Deploy All Things",
                 "commands": [f"dradis deploy all the things {version} to {client_lc} production_{variant}"],
                 "validation": f"https://app-ops.aws.mdx.med/deploys?client={client_lc}&env=production&variant={variant}"})

    validation_client = get_validation_client_name(client_lc)

    plan.append({"heading": "Full Indexing",
                 "commands": [f"dradis index data for {client_lc} production_{variant}"],
                 "validation": f"https://data-prd-{variant}-{validation_client}.aws.mdx.med/index_status"})

    plan.append({"heading": "Referencing",
                 "commands": [f"dradis index reference for {client_lc} production_{variant}"],
                 "validation": f"https://solr-master-prd-{variant}-{validation_client}.aws.mdx.med:8443/solr/reference/select?fq=type%3A%22PlatformSearch%3A%3ADocuments%3A%3AReferenceBatchMeta%22&q=*%3A*&sort=batch_created_at_ds+desc"})

    plan.append({"heading": "Billing Codes",
                 "commands": [f"dradis index billing_codes for {client_lc} production_{variant}"],
                 "validation": f"https://solr-cost-prd-{variant}-{validation_client}.aws.mdx.med:8443/solr/cost/select?fq=type%3A%22PlatformSearch%3A%3ADocuments%3A%3ABillingCode%22&q=*%3A*&sort=batch_created_at_ds+desc"})

    plan.append({"heading": "Solr: Replication",
                 "commands": [f"dradis cap solr:replicate for etl {client_lc} production_{variant} debug"],
                 "validation": f"https://data-prd-{variant}-{validation_client}.aws.mdx.med/replication_status"})

    # ---------------- One Day before Deployment Scale out Steps ----------------
    plan.append({"heading": "One Day before Deployment Scale out Steps", "numbered": False})

    plan.append({"heading": "Freeze Passive", "numbered": True,
                 "commands": [f"dradis freeze {client_lc} production_{variant}"]})

    plan.append({"heading": "Snapshot", "numbered": True,
                 "commands": [f"dradis snapshot {client_lc} production_{variant}"],
                 "validation": f"https://app-ops.aws.mdx.med/snapshots?env=production&client={client_lc}&variant={variant}"})

    plan.append({"heading": "Scaleout", "numbered": True,
                 "commands": [f"dradis make {client_lc} production_{variant} ready for cutover"],
                 "validation": f"https://app-ops.aws.mdx.med/client_environments?client={client_lc}&env=production&variant={variant}"})

    plan.append({"heading": "Handover to QA", "numbered": True,
                 "commands": [f"Passive production_{variant} is QA ready. Please validate"]})

    # ---------------- Cutover Steps ----------------
    plan.append({"heading": "Cutover Steps", "numbered": False})

    plan.append({"heading": "Swap Variants", "numbered": True,
                 "commands": [f"dradis make variant {variant} active for {client_lc} production"],
                 "validation": f"https://app-ops.aws.mdx.med/sidekiq/scheduled"})

    plan.append({"heading": "Clear Cache", "numbered": True,
                 "commands": [
                     f"dradis clear cache for api {client_lc} production_{variant}",
                     f"dradis clear cache for etl {client_lc} production_{variant}",
                     f"dradis clear cost for {client_lc} production_{variant}"
                 ]})

    # Final Handover with multiline formatting
    final_handover_text = """The cutover process is now complete, and S365 caches have been cleared. Please proceed with validation. \
Kindly allow a few more minutes for any residual errors to settle down. Let us know if you notice any issues. \
Thanks"""
    plan.append({"heading": "Final Handover", "numbered": True,
                 "commands": [final_handover_text]})

    return plan
