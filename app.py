import http
from flask import Flask, request
import requests
from bs4 import BeautifulSoup
import urllib

app = Flask(__name__)

@app.route("/coord", methods=['POST'])
def get_data():
    longitude = request.form['longitude']
    latitude = request.form['latitude']
    payload = {'lon_coord': longitude, 'lat_coord': latitude, 'RiverRegion': "on", "selectAll": "on", "Baseflow": 'on', "ARFParams": 'on',
                "StormLosses": 'on', "TemporalPatterns": 'on', "ArealTemporalPatterns": 'on', "BoMIFD": 'on',  "Preburst": 'on', "OtherPreburst": 'on', "ClimateChange": 'on',}
    request_data = requests.post("https://data.arr-software.org/", data=payload)

    soup = BeautifulSoup(request_data.text)


    data = []
    table = soup.find("table", {"id": "StormLosses_table"})
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele]) # Get rid of empty values
    

    storm_initial_losses = data[1][1]
    storm_continuing_losses = data[2][1]

    text_file_href = "https://data.arr-software.org/" + soup.find("a", {"id": "dlText"}).attrs.get('href')

    payload = {"input_type": "dd", "points": {"points":[[latitude,latitude]]}, "all_design": ""}

    local_filename = "test_file"

    url = "https://reg.bom.gov.au/water/designRainfalls/revised-ifd/services/downloadtable"

    payload = f"input_type=dd&points=%7B%22points%22%3A%5B%5B{latitude}%2C{longitude}%5D%5D%7D&all_design="
    headers = {
        "cookie": "BIGipServer~Production~PROD_REG_TCP80_HTTP_POOL=rd1o00000000000000000000ffff86b2fd88o80",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "insomnia/8.6.0"
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    all_design_rainfalls_csv = response.json()['csv']
    #urllib.request.urlretrieve('https://reg.bom.gov.au/water/designRainfalls/revised-ifd/services/downloadtable', 'foo_file.csv', data=payload)

    # with requests.post('https://reg.bom.gov.au/water/designRainfalls/revised-ifd/services/downloadtable', data=payload, stream=True) as r:
    #     r.raise_for_status()
    #     with open(local_filename, 'wb') as f:
    #         for chunk in r.iter_content(chunk_size=None): 
    #             # If you have chunk encoded response uncomment if
    #             # and set chunk_size parameter to None.
    #             if chunk: 
    #                 f.write(chunk)
    #print(request_data.json())

    #all_design_rainfalls_csv = soup.find("a", {"id": "ifdDownloadAllDesign"}).attrs.get('href')


    response = {
        'storm_initial_losses': storm_initial_losses,
        'storm_continuing_losses': storm_continuing_losses,
        'text_file_href': text_file_href,
        'all_design_rainfalls_csv': all_design_rainfalls_csv
    }

    return response