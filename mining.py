import requests
import json
from openpyxl import Workbook
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import multiprocessing

wb = Workbook()
ws = wb.active


def request():
    url = "https://websites.greeninfo.org/coal_swarm/coal_tracker/application/views/site/trackers_v4.json"
    resp = requests.get(url)
    return json.loads(resp.text).get('features')


def getCoal(eachfeature, title):
    rowdata = []
    properties = eachfeature.get('properties')
    status = properties.get('status')
    if (status == 'shelved') or (status == 'cancelled'):
        wiki_page = properties.get('wiki_page')
        geometry = eachfeature.get('geometry')
        for eachtitle in title:
            if eachtitle == 'coordinates':
                break
            rowdata.append(properties.get(eachtitle))
        coordinates = str(geometry.get('coordinates')[0]) + ',' + str(geometry.get('coordinates')[1])
        rowdata.append(coordinates)
        # i = i + 1
        headers = {'User-Agent': UserAgent().random}
        try:
            res = requests.get(wiki_page, headers=headers, verify=False)
            html = res.text
            soup = BeautifulSoup(html, 'html.parser')
            result = rowdata
            Coal = soup.find("b", string="Type:")
            if Coal is None:
                result.append("-1")
            else:
                Coalli = Coal.find_parent("li")
                if Coalli is None:
                    sibling = str(Coal.next_sibling)
                    if sibling:
                        if sibling != "<br/>":
                            result.append(sibling)
                        else:
                            result.append("-1")
                    else:
                        result.append("-1")
                else:
                    type = Coalli.get_text(' ', strip=True)
                    typeArr = type.split()
                    if (len(typeArr) >= 2):
                        result.append(typeArr[1])
                    else:
                        result.append("-1")
            lowercase_type = soup.find("b", string="Coal type:")
            if lowercase_type is None:
                Coal_type = soup.find("b", string="Coal Type:")
            else:
                Coal_type = lowercase_type

            if Coal_type is None:
                result.append("-1")
            else:
                Coal_type_li = Coal_type.find_parent("li")
                if Coal_type_li is None:
                    sibling = str(Coal_type.next_sibling)
                    if sibling:
                        if sibling != "<br/>":
                            result.append(sibling)
                        else:
                            result.append("-1")
                    else:
                        result.append("-1")
                else:
                    coaltype = Coal_type_li.get_text(' ', strip=True)
                    coaltypeArr = coaltype.split()
                    if len(coaltypeArr) >= 3:
                        result.append(coaltypeArr[2])
                    else:
                        result.append("-1")
            return result
        except requests.exceptions.RequestException as e:
            print(e)
            # rowdata = []
            # properties = eachfeature.get('properties')
            # geometry = eachfeature.get('geometry')
            # for eachtitle in title:
            #     if eachtitle == 'coordinates':
            #         break
            #     rowdata.append(properties.get(eachtitle))
            # coordinates = str(geometry.get('coordinates')[0]) + ',' + str(geometry.get('coordinates')[1])
            # rowdata.append(coordinates)
            # rowdata.append('not ava')
            # rowdata.append('not ava')
            # ws.append(rowdata)
            # print('err')
            # print(rowdata)
            pass


def toExcel(title, features, excelfile):
    ws.append(title)
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    for eachfeature in features:
        result = pool.apply_async(getCoal, (eachfeature, title), callback=tempStore)
    pool.close()
    pool.join()
    # if i == 20:
    #     break
    print('saving')
    wb.save(excelfile)


def tempStore(result):
    if result is not None:
        ws.append(result)


# def handleTitle():
#     title = []


if __name__ == '__main__':
    title = ["unit", "plant", "other_names", "wiki_page", "sponsor", "capacity_mw", "status", "region", "country",
             "subnational_unit", "annual_co2_mtons", "coordinates", "Coal", "Coal type"]
    features = request()
    # features = [{"type": "Feature", "properties": {"unit": "East Hope Metals Wucaiwan power station Unit 3",
    #                                                "plant": "East Hope Metals Wucaiwan power station",
    #                                                "other_names": "", "wiki_page": "http://bit.ly/1toaGrN",
    #                                                "sponsor": "Xinjiang East Hope Non-Ferrous Metal Co Ltd.",
    #                                                "capacity_mw": 350, "status": "operating", "region": "East Asia",
    #                                                "country": "China", "subnational_unit": "Xinjiang",
    #                                                "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [89.113841, 44.688508]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "East Hope Metals Wucaiwan power station Unit 4",
    #                                                "plant": "East Hope Metals Wucaiwan power station",
    #                                                "other_names": "", "wiki_page": "http://bit.ly/1toaGrN",
    #                                                "sponsor": "Xinjiang East Hope Non-Ferrous Metal Co Ltd.",
    #                                                "capacity_mw": 350, "status": "operating", "region": "East Asia",
    #                                                "country": "China", "subnational_unit": "Xinjiang",
    #                                                "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [89.113841, 44.688508]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "East Hope Metals Wucaiwan power station Unit 5",
    #                                                "plant": "East Hope Metals Wucaiwan power station",
    #                                                "other_names": "", "wiki_page": "http://bit.ly/1toaGrN",
    #                                                "sponsor": "Xinjiang East Hope Non-Ferrous Metal Co Ltd.",
    #                                                "capacity_mw": 350, "status": "operating", "region": "East Asia",
    #                                                "country": "China", "subnational_unit": "Xinjiang",
    #                                                "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [89.113841, 44.688508]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "East Hope Metals Wucaiwan power station Unit 6",
    #                                                "plant": "East Hope Metals Wucaiwan power station",
    #                                                "other_names": "", "wiki_page": "http://bit.ly/1toaGrN",
    #                                                "sponsor": "Xinjiang East Hope Non-Ferrous Metal Co Ltd.",
    #                                                "capacity_mw": 350, "status": "operating", "region": "East Asia",
    #                                                "country": "China", "subnational_unit": "Xinjiang",
    #                                                "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [89.113841, 44.688508]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "East Hope Metals Wucaiwan power station Unit 7",
    #                                                "plant": "East Hope Metals Wucaiwan power station",
    #                                                "other_names": "", "wiki_page": "http://bit.ly/1toaGrN",
    #                                                "sponsor": "Xinjiang East Hope Non-Ferrous Metal Co Ltd.",
    #                                                "capacity_mw": 350, "status": "operating", "region": "East Asia",
    #                                                "country": "China", "subnational_unit": "Xinjiang",
    #                                                "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [89.113841, 44.688508]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "East Hope Metals Wucaiwan power station Unit 8",
    #                                                "plant": "East Hope Metals Wucaiwan power station",
    #                                                "other_names": "", "wiki_page": "http://bit.ly/1toaGrN",
    #                                                "sponsor": "Xinjiang East Hope Non-Ferrous Metal Co Ltd.",
    #                                                "capacity_mw": 350, "status": "operating", "region": "East Asia",
    #                                                "country": "China", "subnational_unit": "Xinjiang",
    #                                                "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [89.113841, 44.688508]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "East Hope Metals Wucaiwan power station Unit 9",
    #                                                "plant": "East Hope Metals Wucaiwan power station",
    #                                                "other_names": "", "wiki_page": "http://bit.ly/1toaGrN",
    #                                                "sponsor": "Xinjiang East Hope Non-Ferrous Metal Co Ltd.",
    #                                                "capacity_mw": 350, "status": "operating", "region": "East Asia",
    #                                                "country": "China", "subnational_unit": "Xinjiang",
    #                                                "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [89.113841, 44.688508]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Fuchen Kuqa Cogen power station Unit 1",
    #                                                "plant": "Fuchen Kucha Cogen power station", "other_names": "",
    #                                                "wiki_page": "http://bit.ly/2jqERAX",
    #                                                "sponsor": "Xinjiang Fuchen Power & Energy Co", "capacity_mw": 350,
    #                                                "status": "shelved", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [83.026220, 41.741151]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Fuchen Kuqa Cogen power station Unit 2",
    #                                                "plant": "Fuchen Kucha Cogen power station", "other_names": "",
    #                                                "wiki_page": "http://bit.ly/2jqERAX",
    #                                                "sponsor": "Xinjiang Fuchen Power & Energy Co", "capacity_mw": 350,
    #                                                "status": "shelved", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [83.026220, 41.741151]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Fukang Second Power Plant Unit 1", "plant": "Fukang Second Power Plant",
    #                             "other_names": "", "wiki_page": "http://bit.ly/16oEOvd",
    #                             "sponsor": "Huaneng Xinjiang Energy Dev Co", "capacity_mw": 350, "status": "shelved",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [88.186740, 44.141137]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Fukang Second Power Plant Unit 2", "plant": "Fukang Second Power Plant",
    #                             "other_names": "", "wiki_page": "http://bit.ly/16oEOvd",
    #                             "sponsor": "Huaneng Xinjiang Energy Dev Co", "capacity_mw": 350, "status": "shelved",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [88.186740, 44.141137]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Fukang Yongxiang 1", "plant": "Fukang Yongxiang power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1tq4pwi",
    #                             "sponsor": "Sichuan Yongxiang Co Ltd", "capacity_mw": 350, "status": "cancelled",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.987000, 44.156000]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Fukang Yongxiang 2", "plant": "Fukang Yongxiang power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1tq4pwi",
    #                             "sponsor": "Sichuan Yongxiang Co Ltd", "capacity_mw": 350, "status": "cancelled",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.987000, 44.156000]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Fukang Yongxiang 3", "plant": "Fukang Yongxiang power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1tq4pwi",
    #                             "sponsor": "Sichuan Yongxiang Co Ltd", "capacity_mw": 350, "status": "cancelled",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.987000, 44.156000]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Fukang Yongxiang 4", "plant": "Fukang Yongxiang power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1tq4pwi",
    #                             "sponsor": "Sichuan Yongxiang Co Ltd", "capacity_mw": 350, "status": "cancelled",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.987000, 44.156000]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Fukang Yongxiang 5", "plant": "Fukang Yongxiang power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1tq4pwi",
    #                             "sponsor": "Sichuan Yongxiang Co Ltd", "capacity_mw": 350, "status": "cancelled",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.987000, 44.156000]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Ganquanbao TBEA 1", "plant": "Ganquanbao TBEA power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/ZAunRl",
    #                             "sponsor": "Tbea Xinjiang Silicon Indust", "capacity_mw": 350, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.770718, 44.124707]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Ganquanbao TBEA 2", "plant": "Ganquanbao TBEA power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/ZAunRl",
    #                             "sponsor": "Tbea Xinjiang Silicon Indust", "capacity_mw": 350, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.770718, 44.124707]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Guodian Bachu power station Unit 1", "plant": "Guodian Bachu power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1tq5Lak", "sponsor": "Guodian",
    #                             "capacity_mw": 350, "status": "cancelled", "region": "East Asia", "country": "China",
    #                             "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [78.550000, 39.785000]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Guodian Bachu power station Unit 2", "plant": "Guodian Bachu power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1tq5Lak", "sponsor": "Guodian",
    #                             "capacity_mw": 350, "status": "cancelled", "region": "East Asia", "country": "China",
    #                             "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [78.550000, 39.785000]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Guodian Beitun 3", "plant": "Guodian Beitun power station", "other_names": "",
    #                             "wiki_page": "http://bit.ly/1tpW37Z", "sponsor": "China Guodian Corp",
    #                             "capacity_mw": 330, "status": "cancelled", "region": "East Asia", "country": "China",
    #                             "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.767784, 47.325034]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Guodian Beitun 4", "plant": "Guodian Beitun power station", "other_names": "",
    #                             "wiki_page": "http://bit.ly/1tpW37Z", "sponsor": "China Guodian Corp",
    #                             "capacity_mw": 330, "status": "cancelled", "region": "East Asia", "country": "China",
    #                             "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.767784, 47.325034]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Guodian Dananhu power station Unit 1",
    #                                                "plant": "Guodian Dananhu power station", "other_names": "",
    #                                                "wiki_page": "http://bit.ly/1uJiH6C",
    #                                                "sponsor": "China Guodian Corp", "capacity_mw": 660,
    #                                                "status": "operating", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [93.191405, 42.320246]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Guodian Dananhu power station Unit 2",
    #                                                "plant": "Guodian Dananhu power station", "other_names": "",
    #                                                "wiki_page": "http://bit.ly/1uJiH6C",
    #                                                "sponsor": "China Guodian Corp", "capacity_mw": 660,
    #                                                "status": "operating", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [93.191405, 42.320246]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Guodian Kuqa power station Unit 1", "plant": "Guodian Kuqa power station",
    #                             "other_names": "Kuqa (Kuche) power station", "wiki_page": "http://bit.ly/1JQqqbl",
    #                             "sponsor": "China Guodian Corp", "capacity_mw": 135, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [82.887910, 41.738150]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Guodian Kuqa power station Unit 2", "plant": "Guodian Kuqa power station",
    #                             "other_names": "Kuqa (Kuche) power station", "wiki_page": "http://bit.ly/1JQqqbl",
    #                             "sponsor": "China Guodian Corp", "capacity_mw": 135, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [82.887910, 41.738150]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Guodian Kuqa power station Unit 3", "plant": "Guodian Kuqa power station",
    #                             "other_names": "Kuqa (Kuche) power station", "wiki_page": "http://bit.ly/1uJl0qg",
    #                             "sponsor": "China Guodian Corp", "capacity_mw": 300, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [82.887910, 41.738150]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Guodian Kuqa power station Unit 4", "plant": "Guodian Kuqa power station",
    #                             "other_names": "Kuqa (Kuche) power station", "wiki_page": "http://bit.ly/1uJl0qg",
    #                             "sponsor": "China Guodian Corp", "capacity_mw": 300, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [82.887910, 41.738150]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Guodian Nilka Power Plant Unit 1", "plant": "Guodian Nilka Power Plant",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1z8qq4J",
    #                             "sponsor": "Guodian Xinjiang Power", "capacity_mw": 660, "status": "shelved",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [82.584882, 43.806579]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Guodian Nilka Power Plant Unit 2", "plant": "Guodian Nilka Power Plant",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1z8qq4J",
    #                             "sponsor": "Guodian Xinjiang Power", "capacity_mw": 660, "status": "shelved",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [82.584882, 43.806579]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Guodian Tacheng power station Unit 1",
    #                                                "plant": "Guodian Tacheng power station", "other_names": "",
    #                                                "wiki_page": "http://bit.ly/1qhh3YQ", "sponsor": "China Guodian",
    #                                                "capacity_mw": 660, "status": "cancelled", "region": "East Asia",
    #                                                "country": "China", "subnational_unit": "Xinjiang",
    #                                                "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [82.983333, 46.750000]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Guodian Tacheng power station Unit 2",
    #                                                "plant": "Guodian Tacheng power station", "other_names": "",
    #                                                "wiki_page": "http://bit.ly/1qhh3YQ", "sponsor": "China Guodian",
    #                                                "capacity_mw": 660, "status": "cancelled", "region": "East Asia",
    #                                                "country": "China", "subnational_unit": "Xinjiang",
    #                                                "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [82.983333, 46.750000]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Song Hau-3 Unit 2", "plant": "Song Hau Thermal Power Plant", "other_names": "",
    #                             "wiki_page": "http://bit.ly/1dET5q5", "sponsor": "TBD", "capacity_mw": 1000,
    #                             "status": "cancelled", "region": "SE Asia", "country": "Vietnam",
    #                             "subnational_unit": "Hau Giang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [105.860710, 9.952660]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Guodian Turpan power station Unit 1", "plant": "Guodian Turpan power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1w0aiP2", "sponsor": "China Guodian",
    #                             "capacity_mw": 660, "status": "cancelled", "region": "East Asia", "country": "China",
    #                             "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [89.183333, 42.966667]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Guodian Turpan power station Unit 2", "plant": "Guodian Turpan power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1w0aiP2", "sponsor": "China Guodian",
    #                             "capacity_mw": 660, "status": "cancelled", "region": "East Asia", "country": "China",
    #                             "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [89.183333, 42.966667]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Guotai Xinhua unit 1", "plant": "Guotai Xinhua Coal Chemical power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/2w8reh6",
    #                             "sponsor": "Xinjiang Guotai Xinhua Mining Co", "capacity_mw": 350,
    #                             "status": "construction", "region": "East Asia", "country": "China",
    #                             "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [89.074200, 44.695300]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Guotai Xinhua unit 2", "plant": "Guotai Xinhua Coal Chemical power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/2w8reh6",
    #                             "sponsor": "Xinjiang Guotai Xinhua Mining Co", "capacity_mw": 350,
    #                             "status": "construction", "region": "East Asia", "country": "China",
    #                             "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [89.074200, 44.695300]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Hami Sandaoling Unit 1", "plant": "Hami Sandaoling  power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/2slHskY",
    #                             "sponsor": "Hami Luxin Guoneng Thermal Power Co", "capacity_mw": 350,
    #                             "status": "permitted", "region": "East Asia", "country": "China",
    #                             "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [92.634600, 43.168600]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Hami Sandaoling Unit 2", "plant": "Hami Sandaoling  power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/2slHskY",
    #                             "sponsor": "Hami Luxin Guoneng Thermal Power Co", "capacity_mw": 350,
    #                             "status": "permitted", "region": "East Asia", "country": "China",
    #                             "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [92.634600, 43.168600]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Hefeng 1", "plant": "Hefeng power station",
    #                                                "other_names": "Tacheng power plant",
    #                                                "wiki_page": "http://bit.ly/1sEiOnW",
    #                                                "sponsor": "Shenhua Guoneng Energy Group", "capacity_mw": 300,
    #                                                "status": "operating", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [86.593600, 46.608800]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Hefeng 2", "plant": "Hefeng power station",
    #                                                "other_names": "Tacheng power plant",
    #                                                "wiki_page": "http://bit.ly/1sEiOnW",
    #                                                "sponsor": "Shenhua Guoneng Energy Group", "capacity_mw": 300,
    #                                                "status": "operating", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [86.593600, 46.608800]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Hefeng 3", "plant": "Hefeng power station",
    #                                                "other_names": "Shenhua Tacheng power station",
    #                                                "wiki_page": "http://bit.ly/1sEiOnW",
    #                                                "sponsor": "Shenhua Guoneng Energy Group", "capacity_mw": 660,
    #                                                "status": "shelved", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [86.593600, 46.608800]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Hefeng 4", "plant": "Hefeng power station",
    #                                                "other_names": "Shenhua Tacheng power station",
    #                                                "wiki_page": "http://bit.ly/1sEiOnW",
    #                                                "sponsor": "Shenhua Guoneng Energy Group", "capacity_mw": 660,
    #                                                "status": "shelved", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [86.593600, 46.608800]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Henglian Wucaiwan 1", "plant": "Henglian Wucaiwan power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1ptWIkZ",
    #                             "sponsor": "Xinjiang Henglian Energy Co", "capacity_mw": 660, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [89.197700, 44.789600]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Henglian Wucaiwan 2", "plant": "Henglian Wucaiwan power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1ptWIkZ",
    #                             "sponsor": "Xinjiang Henglian Energy Co", "capacity_mw": 660, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [89.197700, 44.789600]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Henglian Wucaiwan 3", "plant": "Henglian Wucaiwan power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1ptWIkZ",
    #                             "sponsor": "China Shenhua Energy Co Ltd", "capacity_mw": 660, "status": "cancelled",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [89.197700, 44.789600]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Henglian Wucaiwan 4", "plant": "Henglian Wucaiwan power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1ptWIkZ",
    #                             "sponsor": "China Shenhua Energy Co Ltd", "capacity_mw": 660, "status": "cancelled",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [89.197700, 44.789600]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Hesheng Shanshan power station Unit 1",
    #                                                "plant": "Hesheng Shanshan power station", "other_names": "",
    #                                                "wiki_page": "http://bit.ly/2af9vd3",
    #                                                "sponsor": "Hesheng Silicon Industry Co", "capacity_mw": 330,
    #                                                "status": "operating", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [86.098411, 44.455971]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Hesheng Shanshan power station Unit 2",
    #                                                "plant": "Hesheng Shanshan power station", "other_names": "",
    #                                                "wiki_page": "http://bit.ly/2af9vd3",
    #                                                "sponsor": "Hesheng Silicon Industry Co", "capacity_mw": 330,
    #                                                "status": "operating", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [86.098411, 44.455971]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Hesheng Shanshan power station Unit 3",
    #                                                "plant": "Hesheng Shanshan power station", "other_names": "",
    #                                                "wiki_page": "http://bit.ly/2af9vd3",
    #                                                "sponsor": "Hesheng Silicon Industry Co", "capacity_mw": 350,
    #                                                "status": "construction", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [90.126799, 42.974907]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Hesheng Shanshan power station Unit 4",
    #                                                "plant": "Hesheng Shanshan power station", "other_names": "",
    #                                                "wiki_page": "http://bit.ly/2af9vd3",
    #                                                "sponsor": "Hesheng Silicon Industry Co", "capacity_mw": 350,
    #                                                "status": "construction", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [90.126799, 42.974907]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Hesheng Shanshan power station Unit 5",
    #                                                "plant": "Hesheng Shanshan power station", "other_names": "",
    #                                                "wiki_page": "http://bit.ly/2af9vd3",
    #                                                "sponsor": "Hesheng Silicon Industry Co", "capacity_mw": 350,
    #                                                "status": "announced", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [90.126799, 42.974907]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Hongxing Cogen Captive power station Unit 1",
    #                                                "plant": "Hongxing Cogen Captive power station", "other_names": "",
    #                                                "wiki_page": "http://bit.ly/2vHitGu",
    #                                                "sponsor": "Hongxing Heating Co", "capacity_mw": 350,
    #                                                "status": "construction", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [94.118000, 42.537700]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Hongxing Cogen Captive power station Unit 2",
    #                                                "plant": "Hongxing Cogen Captive power station", "other_names": "",
    #                                                "wiki_page": "http://bit.ly/2vHitGu",
    #                                                "sponsor": "Hongxing Heating Co", "capacity_mw": 350,
    #                                                "status": "construction", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [94.118000, 42.537700]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Hongyanchi-1 power station Unit 10", "plant": "Hongyanchi-1 power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1s7zgLr",
    #                             "sponsor": "China Guodian Corp", "capacity_mw": 330, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.629356, 43.728065]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Hongyanchi-1 power station Unit 11", "plant": "Hongyanchi-1 power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1s7zgLr",
    #                             "sponsor": "China Guodian Corp", "capacity_mw": 330, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.629356, 43.728065]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Hongyanchi-1 power station Unit 12", "plant": "Hongyanchi-1 power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1s7zgLr",
    #                             "sponsor": "China Guodian Corp", "capacity_mw": 330, "status": "cancelled",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.629356, 43.728065]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Hongyanchi-1 power station Unit 13", "plant": "Hongyanchi-1 power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1s7zgLr",
    #                             "sponsor": "China Guodian Corp", "capacity_mw": 330, "status": "cancelled",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.629356, 43.728065]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Hongyanchi-1 power station Unit 5", "plant": "Hongyanchi-1 power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1MulZIk",
    #                             "sponsor": "China Guodian Corp", "capacity_mw": 55, "status": "retired",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.629356, 43.728065]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Hongyanchi-1 power station Unit 6", "plant": "Hongyanchi-1 power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1MulZIk",
    #                             "sponsor": "China Guodian Corp", "capacity_mw": 55, "status": "retired",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.629356, 43.728065]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Hongyanchi-1 power station Unit 7", "plant": "Hongyanchi-1 power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1MulZIk",
    #                             "sponsor": "China Guodian Corp", "capacity_mw": 50, "status": "retired",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.629356, 43.728065]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Hongyanchi-1 power station Unit 8", "plant": "Hongyanchi-1 power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1MulZIk",
    #                             "sponsor": "China Guodian Corp", "capacity_mw": 50, "status": "retired",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.629356, 43.728065]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Hongyanchi-1 power station Unit 9", "plant": "Hongyanchi-1 power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1MulZIk",
    #                             "sponsor": "China Guodian Corp", "capacity_mw": 110, "status": "retired",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.629356, 43.728065]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Hongyanchi-2 power station Unit 1", "plant": "Hongyanchi-2 power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1Mumkuo",
    #                             "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 200, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.657498, 43.743243]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Hongyanchi-2 power station Unit 2", "plant": "Hongyanchi-2 power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1Mumkuo",
    #                             "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 200, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.657498, 43.743243]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Hongyanchi-2 power station Unit 3", "plant": "Hongyanchi-2 power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1Mumkuo",
    #                             "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 200, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.657498, 43.743243]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Hongyanchi-2 power station Unit 4", "plant": "Hongyanchi-2 power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1Mumkuo",
    #                             "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 200, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.657498, 43.743243]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Hongyanchi-2 power station Unit 5", "plant": "Hongyanchi-2 power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1AE3ISe",
    #                             "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 330, "status": "cancelled",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.657498, 43.743243]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Hongyanchi-2 power station Unit 6", "plant": "Hongyanchi-2 power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1AE3ISe",
    #                             "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 330, "status": "cancelled",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.657498, 43.743243]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Huadian Changji power station Unit 3",
    #                                                "plant": "Huadian Changji power station", "other_names": "",
    #                                                "wiki_page": "http://bit.ly/1IIpkDR",
    #                                                "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 125,
    #                                                "status": "retired", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.311490, 43.991440]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Huadian Changji power station Unit 4",
    #                                                "plant": "Huadian Changji power station", "other_names": "",
    #                                                "wiki_page": "http://bit.ly/1IIpkDR",
    #                                                "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 125,
    #                                                "status": "retired", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.311490, 43.991440]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Huadian Changji power station Unit 5",
    #                                                "plant": "Huadian Changji power station", "other_names": "",
    #                                                "wiki_page": "http://bit.ly/12452kG",
    #                                                "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 330,
    #                                                "status": "operating", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.326558, 44.063250]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Huadian Changji power station Unit 6",
    #                                                "plant": "Huadian Changji power station", "other_names": "",
    #                                                "wiki_page": "http://bit.ly/12452kG",
    #                                                "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 330,
    #                                                "status": "operating", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [87.326558, 44.063250]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Huadian Hami Power Station Unit 5", "plant": "Huadian Hami power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1MJcU0w",
    #                             "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 135, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [93.440788, 42.893385]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Huadian Hami Power Station Unit 6", "plant": "Huadian Hami power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1MJcU0w",
    #                             "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 135, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [93.440788, 42.893385]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Huadian Hami Power Station Unit 7", "plant": "Huadian Hami power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1MJcU0w",
    #                             "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 350,
    #                             "status": "construction", "region": "East Asia", "country": "China",
    #                             "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [93.440788, 42.893385]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Huadian Hami Power Station Unit 8", "plant": "Huadian Hami power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1MJcU0w",
    #                             "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 350,
    #                             "status": "construction", "region": "East Asia", "country": "China",
    #                             "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [93.440788, 42.893385]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Huadian Kashi power station Unit 1", "plant": "Huadian Kashi power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1MufCof",
    #                             "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 50, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [76.049852, 39.481570]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Huadian Kashi power station Unit 2", "plant": "Huadian Kashi power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1MufCof",
    #                             "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 50, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [76.049852, 39.481570]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Huadian Kashi power station Unit 3", "plant": "Huadian Kashi power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1MufCof",
    #                             "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 50, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [76.049852, 39.481570]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Huadian Kashi power station Unit 4", "plant": "Huadian Kashi power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1MufCof",
    #                             "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 50, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [76.049852, 39.481570]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Huadian Kashi power station Unit 5", "plant": "Huadian Kashi power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1pMlhab",
    #                             "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 350, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [76.049852, 39.481570]}}
    #     ,
    #             {"type": "Feature",
    #              "properties": {"unit": "Huadian Kashi power station Unit 6", "plant": "Huadian Kashi power station",
    #                             "other_names": "", "wiki_page": "http://bit.ly/1pMlhab",
    #                             "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 350, "status": "operating",
    #                             "region": "East Asia", "country": "China", "subnational_unit": "Xinjiang",
    #                             "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [76.049852, 39.481570]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Huadian Shawan Cogen power station Unit 1",
    #                                                "plant": "Huadian Shawan Cogen power station", "other_names": "",
    #                                                "wiki_page": "http://bit.ly/2jZcJFx",
    #                                                "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 350,
    #                                                "status": "shelved", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [85.603456, 44.309987]}}
    #     ,
    #             {"type": "Feature", "properties": {"unit": "Huadian Shawan Cogen power station Unit 2",
    #                                                "plant": "Huadian Shawan Cogen power station", "other_names": "",
    #                                                "wiki_page": "http://bit.ly/2jZcJFx",
    #                                                "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 350,
    #                                                "status": "shelved", "region": "East Asia", "country": "China",
    #                                                "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #              "geometry": {"type": "Point", "coordinates": [85.603456, 44.309987]}}
    #     , ]
    toExcel(title, features, './multicoalmining.xlsx')
    # c = ["00","11"]
    # feature = {"type": "Feature", "properties": {"unit": "Huadian Shawan Cogen power station Unit 2",
    #                                              "plant": "Huadian Shawan Cogen power station", "other_names": "",
    #                                              "wiki_page": "https://www.sourcewatch.org/index.php/Larsen_&_Tubro_power_station",
    #                                              "sponsor": "Huadian Xinjiang Power Co Ltd", "capacity_mw": 350,
    #                                              "status": "shelved", "region": "East Asia", "country": "China",
    #                                              "subnational_unit": "Xinjiang", "annual_co2_mtons": 0.000000},
    #            "geometry": {"type": "Point", "coordinates": [85.603456, 44.309987]}}
    # resu = getCoal(feature, title)
    # if resu is None:
    #     title.append('-2')
    #     title.append('-2')
    #     for s in title:
    #         print(s)
    # else:
    #     for s in resu:
    #         print(s)
