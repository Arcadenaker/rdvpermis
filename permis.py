import requests
from datetime import date
from datetime import datetime
from loguru import logger


# Constantes
REGISTRATION_TYPE = "rQj2a"
DATE = date.today()
URL_DATE = f"https://rendezvous.permisconduire.be/api/frontend/v4/offers/_calendar?afterDate={DATE.year}-{DATE.month:02d}-{DATE.day:02d}&size=40&sites=SITE_ID&types={REGISTRATION_TYPE}"
URL_HOUR = f"https://rendezvous.permisconduire.be/api/frontend/v4/offers/_hours?type={REGISTRATION_TYPE}&sites=SITE_ID&date=DATET00:00"
URL_SITES = f"https://rendezvous.permisconduire.be/api/frontend/v4/sites"


logger.info("Looking up all sites")
request_sites = requests.get(URL_SITES)
data = request_sites.json()

for site in data["contents"]:
    site_name = site["externalLabel"]["fr"]
    logger.info("Looking up for " + site_name)

    request_date = requests.get(URL_DATE.replace("SITE_ID", site["id"]))
    data = request_date.json()
    date_request_status = request_date.status_code

    if date_request_status != 200:
        requests.post("https://ntfy.sh/permis_horaciooo",
        data=f"URL_DATE envoie une erreur: {date_request_status}".encode(encoding='utf-8'),
         headers={
            "Title": "Erreur".encode(encoding='utf-8'),
            "Priority": "5",
            "Tags": "rotating_light",
         })
        print("Code d'erreur pour la date:", date_request_status)
        exit()
    for day in data["days"]:
        if day["hasOfferMatchingRestriction"]:
            url = URL_HOUR.replace("DATE", day["day"]).replace("SITE_ID", site["id"]) 
            request_hour = requests.get(url)
            data2 = request_hour.json()
            hour_request_status = request_hour.status_code
            if hour_request_status != 200:
                requests.post("https://ntfy.sh/permis_horaciooo",
                data=f"URL_HOUR envoie une erreur: {date_request_status}".encode(encoding='utf-8'),
                headers={
                    "Title": "Erreur".encode(encoding='utf-8'),
                    "Priority": "5",
                    "Tags": "rotating_light",
                })
                print("Code d'erreur pour la date:", hour_request_status)
                exit()

            already_annonced = False

            for date in data2:
                available_dates = []
                try:
                    with open("rdv.txt", "r") as file:
                        available_dates = file.read().splitlines()
                    #Vérifie si le rdv n'a pas déjà été vérifié précédemment
                    for rdv in available_dates:
                        if rdv == date["date"]:
                            already_annonced = True
                            continue
                        available_dates.remove(rdv)

                except:
                    pass
            
                if already_annonced:
                    #Passe alors à la prochaine date disponible
                    continue
            
                #Si nouvelle date alors il l'ajoute au registre
                available_dates.append(date["date"])

                with open("rdv.txt", "w") as file:
                    file.write("\n".join(available_dates))

                datetime_obj = datetime.strptime(date["date"],"%Y-%m-%dT%H:%M:%S")
                month = datetime_obj.strftime("%m")
                day = datetime_obj.strftime("%d")
                weekday = datetime_obj.strftime("%A")
                hour = datetime_obj.strftime("%H")
                minute = datetime_obj.strftime("%M")
            
                requests.post("https://ntfy.sh/permis_horaciooo",
                    data=(f"Un rendez-vous est disponible le {day}/{month} ({weekday}) à {hour}h{minute} au "+site_name).encode(encoding='utf-8'),
                    headers={
                        "Title": "Rendez-vous permis".encode(encoding='utf-8'),
                        "Priority": "5",
                        "Tags": "loudspeaker",
                        "Click": "https://rendezvous.permisconduire.be/home/"
                    })
                print(f"Un rendez-vous est disponible le {day}/{month} ({weekday}) à {hour}h{minute} au "+site_name)
            
print("Scan Terminé.")
