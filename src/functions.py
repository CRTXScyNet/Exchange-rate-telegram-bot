import json
import os.path
from idlelib.configdialog import changes
from statistics import correlation

from PIL.ImImagePlugin import split
from requests import request, get
from win32ctypes.pywin32.pywintypes import datetime


filepath = 'data.json'


def write(my_dict: dict):
    """Write dictionary as json to file"""
    with open(filepath, 'w') as f:
        json.dump(my_dict, f)


def read() -> dict:
    """Read data from the file"""
    data = {}

    with open(filepath) as f:
        data = json.load(f)

    return data


def download_rates() -> dict:
    """Download rates from remote API"""
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    my_dict = {}

    response = get(url)

    for rate in response.json()['Valute']:
        my_dict[rate] = response.json()['Valute'][rate]['Value']

    return my_dict


def convert_to_string(my_dict: dict) -> str:
    """Convert dict to a human friendly string"""
    message = ''
    for k, v in my_dict.items():
        message += f"{k}: {v}\n"

    return message.strip()


def check_changes() -> dict:
    """Check changes between local and remote datas"""
    changed_dict = {}
    local_dict = {}

    if os.path.exists(filepath):
        local_dict = read()

    remote_dict = download_rates()

    for local in local_dict:
        remote = remote_dict[local]
        if local_dict[local] != remote:
            changed_dict[local] = remote

    write(remote_dict)

    return changed_dict


def get_rate() -> str:
    """Return changed currency or empty string if changed not found"""
    changed_dict = check_changes()

    print(f'Length of changes: {len(changed_dict)}')

    custom_format = '%H:%M'
    cur_time = datetime.now().time()
    print(f'Time: {cur_time.strftime(custom_format)}')

    return convert_to_string(changed_dict)

def get_custom_currency(rates:str='') -> str:

    """Returns custom currency wrote in str argument,"""
    rates = rates.strip().upper().splitlines()
    if not os.path.exists(filepath):
        check_changes()

    for i in range(len(rates)):
        rates[i] = rates[i].strip()
        rates.extend(rates[i].split(','))
        rates[i] = ''

    for i in range(len(rates)):
        s1 = rates[i].strip()
        if ' ' in s1:
            s1 = s1.split()
            for i2 in range(len(s1)):
                s2 = s1[i2].strip()
                s1[i2] = s2
                rates.insert(len(rates),s2)
            rates[i] = ''
        else:
            rates[i] = s1




    local_dict = read()
    rates = [i for i in rates if i != '']
    message = {}
    for rate in rates:
        if rate in local_dict:
            message[rate] = local_dict[rate]

    message = convert_to_string(message)

    return message

def get_all_currencies() -> str:
    """Returns all available currencies"""
    if not os.path.exists(filepath):
        check_changes()

    result = convert_to_string(read())

    return result