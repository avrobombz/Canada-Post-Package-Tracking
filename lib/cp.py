import requests
import json

def cp_pull(tracking_number):
    url_start = "https://www.canadapost-postescanada.ca/track-reperage/rs/track/json/package/"
    url_end = "/detail"

    url = url_start + tracking_number + url_end
    r = requests.get(url)
    d = json.loads(r.text)

    x = {}
    loop = {}
    l = []

    x['pin'] = d['pin']
    try:
        x['prod'] = d['productNmEn']
    except:
        x['prod'] = None
    try: 
        x['status'] = d['status']
    except:
        x['status'] = 'Not Scanned'
    try:
        x['delivered'] = d['delivered']
    except:
        x['delivered'] = False
    try:
        x['destination'] = d['addtnlDestInfo']
    except:
        x['destination'] = None

    try: 
        events = d['events']

        for i in range(len(events)):
            loop['location'] = events[i]['locationAddr']['city']
            loop['status'] = events[i]['descEn']
            l.append(loop.copy())
    except:
        events = [] #left off, return location/status as null on exception
    return (x,l)
