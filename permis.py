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


def get_appointments():
    
    app = {}

    logger.info("Looking up all sites")
    request_sites = requests.get(URL_SITES)
    data = request_sites.json()
    
    for site in data["contents"]:
        site_name = site["externalLabel"]["fr"]
        app[site_name] = []
        logger.info("Looking up for " + site_name)

        request_date = requests.get(URL_DATE.replace("SITE_ID", site["id"]))
        data = request_date.json()
        date_request_status = request_date.status_code

        if date_request_status != 200:
            logger.error("Code d'erreur pour la date:", date_request_status)
            exit()

        for day in data["days"]:
            if day["hasOfferMatchingRestriction"]:
                url = URL_HOUR.replace("DATE", day["day"]).replace("SITE_ID", site["id"]) 
                request_hour = requests.get(url)
                data2 = request_hour.json()
                hour_request_status = request_hour.status_code
                if hour_request_status != 200:
                    logger.error("Code d'erreur pour la date:", hour_request_status)
                    exit()

                already_annonced = False

                for date in data2:
            
                    #Si nouvelle date alors il l'ajoute au registre
                    app[site_name].append(date["date"])


                    datetime_obj = datetime.strptime(date["date"],"%Y-%m-%dT%H:%M:%S")
                    month = datetime_obj.strftime("%m")
                    day = datetime_obj.strftime("%d")
                    weekday = datetime_obj.strftime("%A")
                    hour = datetime_obj.strftime("%H")
                    minute = datetime_obj.strftime("%M")
            
            
    logger.info("Scan Terminé.")
    return app

