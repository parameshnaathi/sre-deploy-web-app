# config.py
# Configuration: valid clients and aliases

VALID_CLIENTS = [
    "nhp", "avmed", "bcbsks", "bcbsla", "bcbsma", "bcbsnc", "bcbsri", "bcbssc", "bcbst", "bcbsvt",
    "bcid", "bluekc", "brighton", "carefirst", "centene", "cobaltblue", "tpa", "ers", "fallon",
    "hcsc", "hcsclabor", "healthcomp", "highmark", "hmsa", "horizon", "kpwa", "kpco", "kpga",
    "kpnw", "lifewise", "medxoom", "moda", "molina", "firstchoice", "pai", "personify", "premera",
    "sandbox", "selecthealth", "sharedhealthms", "texicare", "triples", "trs"
] 

CLIENT_ALIASES = {
    # NHP and its aliases
    "nhp": "nhp", "ahp": "nhp", "allways": "nhp", "mgbhp": "nhp",
    # TPA and its aliases
    "tpa": "tpa", "enterprise": "tpa", "allied benefits": "tpa", "benesys": "tpa", "cox health": "tpa", "united here health": "tpa", "pba": "tpa", "wellfleet": "tpa", "summacare": "tpa",
    # Healthcomp and its alias
    "healthcomp": "healthcomp", "personify": "healthcomp"
}
