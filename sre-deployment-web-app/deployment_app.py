from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from typing import Optional

app = FastAPI()

# Master valid clients
VALID_CLIENTS = {
    "nhp", "avmed", "bcbsks", "bcbsla", "bcbsma", "bcbsnc", "bcbsri",
    "bcbssc", "bcbst", "bcbsvt", "bcid", "bluekc", "brighton", "carefirst",
    "centene", "cobaltblue", "tpa", "ers", "fallon", "hcsc", "hcscLabor",
    "healthcomp", "highmark", "hmsa", "horizon", "kpwa", "kpco", "kpga",
    "kpnw", "lifewise", "medxoom", "moda", "molina", "firstchoice", "pai",
    "personify", "premera", "sandbox", "selecthealth", "sharedhealthms",
    "texicare", "triples", "trs"
}

# Aliases mapping
ALIASES = {
    "ahp": "nhp", "allways": "nhp", "mgbhp": "nhp",
    "enterprise": "tpa", "allied benefits": "tpa", "benesys": "tpa",
    "cox health": "tpa", "united here health": "tpa", "pba": "tpa",
    "wellfleet": "tpa", "summacare": "tpa",
    "healthcomp": "personify"
}

def normalize_client(client: str) -> Optional[str]:
    """
    Normalize client input:
    - lowercase
    - check aliases
    - return main client name if valid
    """
    client_lower = client.strip().lower()
    if client_lower in VALID_CLIENTS:
        return client_lower
    if client_lower in ALIASES:
        return ALIASES[client_lower]
    return None

@app.get("/validate-client/")
async def validate_client(client: str = Query(..., description="Enter client name")):
    normalized = normalize_client(client)
    if not normalized:
        return JSONResponse(status_code=400, content={"error": "Invalid client. Please enter a valid client."})
    return {"valid_client": normalized.upper()}

@app.get("/generate-commands/")
async def generate_commands(
    client: str = Query(..., description="Enter client name"),
    variant: str = Query(..., description="Deployment variant (a or b)")
):
    normalized = normalize_client(client)
    if not normalized:
        return JSONResponse(status_code=400, content={"error": "Invalid client. Please enter a valid client."})

    if variant.lower() not in {"a", "b"}:
        return JSONResponse(status_code=400, content={"error": "Invalid variant. Please choose 'a' or 'b'."})

    commands = [
        f"echo Running pre-deployment checks for {normalized.upper()} Variant {variant.upper()}",
        f"kubectl get pods -n {normalized}-namespace",
        f"kubectl describe deployment {normalized}-app-variant-{variant.lower()}",
        f"echo Deployment steps executed for {normalized.upper()} Variant {variant.upper()}"
    ]
    return {"client": normalized.upper(), "variant": variant.lower(), "commands": commands}