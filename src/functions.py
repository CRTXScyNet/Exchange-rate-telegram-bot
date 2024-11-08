import json
import os.path

from requests import request, get
from win32ctypes.pywin32.pywintypes import datetime

filepath = 'data.json'


def write(my_dict: dict):
    """Write dictionary as json to file"""
    with open(filepath, 'w') as f:
        json.dump(my_dict,f)

def download_rates() -> dict:
    """Download rates from remote API"""
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    my_dict = {}

    response = get(url)

    for rate in response.json()['Valute']:
        my_dict[rate] = response.json()['Valute'][rate]['Value']

    return my_dict

def get_rate():
    my_dict = {}
    changed_dict = {}
    if not os.path.exists(filepath):
        my_dict = download_rates()
        write(my_dict)
        changed_dict =  my_dict.copy()

    print(changed_dict)

get_rate()