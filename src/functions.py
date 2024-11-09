import json
import os.path
from datetime import time

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


def get_rate() -> str:
    my_dict = {}
    changed_dict = {}
    response = download_rates()
    if not os.path.exists(filepath):
        write(response)
        changed_dict = response.copy()
    else:
        my_dict = read()
        for local in my_dict:
            remote = response[local]
            if my_dict[local] != remote:
                changed_dict[local] = remote
            # for remote in response:
            #     if local == remote:
            #         if my_dict[local] != response[remote]:
            #             changed_dict[remote] = response[remote]
            #         continue
    print(f'Length of downloaded dict: {len(response)}')
    print(f'Length of dict of changes: {len(changed_dict)}')
    custom_format = '%H:%M'
    cur_time = datetime.now().time()
    print(f'Time: {cur_time.strftime(custom_format)}')

    if my_dict != response:
        write(response)
        return convert_to_string(changed_dict)
    else:
        return ''
