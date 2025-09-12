AUTHORIZED_USERS = {
    "paramesh.nathi@zelis.com": ("Paramesh", "Nathi"),
    "amroz.syed@zelis.com": ("Amroz", "Syed"),
    "suryateja.varanasi@zelis.com": ("Surya Teja", "Varanasi"),
    "emmadi.haritha@zelis.com": ("Haritha", "Emmadi"),
    "harika.kurnoolu@zelis.com": ("Harika", "Kurnoolu"),
    "bimalkumar.patel@zelis.com": ("Bimalkumar", "Patel"),
    "mohan.budhram@zelis.com": ("Mohan", "Budhram"),
    "daniel.gallegos@zelis.com": ("Daniel", "Gallegos"),
    "arunmai.gummadavalli@zelis.com": ("Arunmai", "Gummadavalli"),
    "michael.pakulak@zelis.com": ("Michael", "Pakulak"),
    "mamadou.barry@zelis.com": ("Mamadou", "Barry"),
    "robin.curry@zelis.com": ("Robin", "Curry"),
    "sridevi.dandu@zelis.com": ("Sridevi", "Dandu"),
}

def is_authorized(email):
    if not isinstance(email, str):
        return False
    return email.strip().lower() in AUTHORIZED_USERS

def get_user_fullname(email):
    if not isinstance(email, str):
        return None, None
    info = AUTHORIZED_USERS.get(email.strip().lower())
    if info:
        return info[0], info[1]
    return None, None