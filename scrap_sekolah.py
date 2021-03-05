from bs4 import BeautifulSoup
import requests
import json

data = []
total_sekolah = 0

page = requests.get('https://referensi.data.kemdikbud.go.id/index11.php')
soup = BeautifulSoup(page.text, 'html.parser', from_encoding="UTF-8")

# collect zones

print("scrapping provinsi")
if page.status_code == 200:
    id = 0
    for i, tr in enumerate(soup.find_all('tr')):
        if i<3:continue
        value = tr.find_all('td')[1].find('a')
        if value is not None:
            id+=1
            value = value.renderContents().decode('UTF-8').strip()
            data.append({
                'id': str(id),
                'value': value,
                'kota': []
            })
            print(value)

print("scraping kab/kota")
for index_provinsi, provinsi in enumerate(data):
    provinsi_id = provinsi['id']
    page = requests.get('https://referensi.data.kemdikbud.go.id/index11.php?kode='+provinsi_id.zfill(2)+"0000&level=1")
    soup = BeautifulSoup(page.text, 'html.parser', from_encoding="UTF-8")
    if page.status_code == 200:
        id = 0
        for i, tr in enumerate(soup.find_all('tr')):
            if i < 3: continue
            value = tr.find_all('td')[1].find('a')
            if value is not None:
                id += 1
                value = value.renderContents().decode('UTF-8').strip()
                data[index_provinsi]['kota'].append({
                    'id': str(id),
                    'value': value,
                    'kecamatan': []
                })
                print(value)

for index_provinsi, provinsi in enumerate(data):
    provinsi_id = provinsi['id']
    for index_kota, kota in enumerate(provinsi['kota']):
        kota_id = kota['id']
        page = requests.get('https://referensi.data.kemdikbud.go.id/index11.php?kode=' + provinsi_id.zfill(2) + kota_id.zfill(2) + "00&level=2")
        soup = BeautifulSoup(page.text, 'html.parser', from_encoding="UTF-8")
        if page.status_code == 200:
            id = 0
            for i, tr in enumerate(soup.find_all('tr')):
                if i < 3: continue
                value = tr.find_all('td')[1].find('a')
                if value is not None:
                    id += 1
                    value = value.renderContents().decode('UTF-8').strip()
                    data[index_provinsi]['kota'][index_kota]['kecamatan'].append({
                        'id': str(id),
                        'value': value,
                        'sekolah': []
                    })
                    print(value)

# create checkpoint
# store zones as json file
json.dump(data, open("zones.json", "w"))

# resume checkpoint
# with open('zones.json') as JSON:
#     data = json.load(JSON)

print("scraping sekolah")
for index_provinsi, provinsi in enumerate(data):
    provinsi_id = provinsi['id']
    for index_kota, kota in enumerate(provinsi['kota']):
        kota_id = kota['id']
        for index_kecamatan, kecamatan in enumerate(kota['kecamatan']):
            kecamatan_id = kecamatan['id']

            #remove _sma from url to get all data

            page = requests.get('https://referensi.data.kemdikbud.go.id/index11_sma.php?kode=' + provinsi_id.zfill(2) + kota_id.zfill(2) + kecamatan_id.zfill(2) + "&level=3")
            soup = BeautifulSoup(page.text, 'html.parser', from_encoding="UTF-8")
            for i, tr in enumerate(soup.find_all('tr')):
                if i < 3:
                    continue
                try:
                    npsn = tr.find_all('td')[1].find('a').find('b').renderContents().decode('utf-8')
                    nama = tr.find_all('td')[2].renderContents().decode('utf-8')
                    alamat = tr.find_all('td')[3].renderContents().decode('utf-8')
                    data[index_provinsi]['kota'][index_kota]['kecamatan'][index_kecamatan]['sekolah'].append({nama, npsn, alamat})
                    total_sekolah += 1
                    print("scraped ", str(total_sekolah))
                except:
                    pass
json.dump(data, open("sekolah.json", "w"))