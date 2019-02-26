import requests
import json
from openpyxl import Workbook
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import urllib.request

wb = Workbook()
ws = wb.active


def request():
    url = "https://websites.greeninfo.org/coal_swarm/coal_tracker/application/views/site/trackers_v4.json"
    resp = requests.get(url)
    return json.loads(resp.text).get('features')


def getCoal(url,rowdata):
    # headers ={"User-Agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Mobile Safari/537.36"}
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            'User-Agent': UserAgent().random
        }
    )
    res = urllib.request.urlopen(req)
    html = res.read()
    soup = BeautifulSoup(html, 'html.parser')
    result = rowdata
    Coal = soup.find("b", string="Type:")
    if Coal is None:
        result.append("-1")
    else:
        Coalli = Coal.find_parent("li")
        if Coalli is None:
            result.append("-1")
        else:
            type = Coalli.get_text(' ', strip=True)
            typeArr = type.split()
            if (len(typeArr) == 2):
                result.append(typeArr[1])
            else:
                result.append("-1")
    Coal_type = soup.find("b", string="Coal type:")
    if Coal_type is None:
        result.append("-1")
    else:
        Coal_type_li = Coal_type.find_parent("li")
        if Coal_type_li is None:
            result.append("-1")
        else:
            coaltype = Coal_type_li.get_text(' ', strip=True)
            coaltypeArr = coaltype.split()
            if len(coaltypeArr) == 3:
                result.append(coaltypeArr[2])
            else:
                result.append("-1")
    return result


def toExcel(title, features, excelfile):
    ws.append(title)
    for eachfeature in features:
        rowdata = []
        properties = eachfeature.get('properties')
        status = properties.get('status')
        if (status == 'shelved') or (status == 'cancelled'):
            wiki_page = properties.get('wiki_page')
            geometry = eachfeature.get('geometry')
            for eachtitle in title:
                rowdata.append(properties.get(eachtitle))
            coordinates = str(geometry.get('coordinates')[0]) + ',' + str(geometry.get('coordinates')[1])
            rowdata.append(coordinates)
            rowdata = getCoal(wiki_page,rowdata)
            ws.append(rowdata)
    print('saving')
    wb.save(excelfile)


# def handleTitle():
#     title = []


if __name__ == '__main__':
    title = ["unit", "plant", "other_names", "wiki_page", "sponsor", "capacity_mw", "status", "region", "country",
             "subnational_unit", "annual_co2_mtons", "coordinates", "Coal", "Coal type"]
    features = request()
    toExcel(title, features, './coalmining.xlsx')
