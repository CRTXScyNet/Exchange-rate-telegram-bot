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


def check_changes(local_dict:dict = None, remote_dict:dict = None) -> dict:
    """Check changes between local and remote datas"""
    changed_dict = {}
    is_write = False
    if local_dict is None:
        local_dict = read()
    if remote_dict is None:
        remote_dict = download_rates()
        is_write = True

    for local in local_dict:
        remote = remote_dict[local]
        if local_dict[local] != remote:
            changed_dict[local] = remote

    if is_write:
        write(remote_dict)

    return changed_dict


def get_rate() -> str:
    local_dict = {}
    changed_dict = {}
    remote_dict = download_rates()
    if not os.path.exists(filepath):
        write(remote_dict)
        changed_dict = remote_dict.copy()
    else:
        local_dict = read()
        check_changes(local_dict,remote_dict)

    print(f'Length of downloaded dict: {len(remote_dict)}')
    print(f'Length of dict of changes: {len(changed_dict)}')
    custom_format = '%H:%M'
    cur_time = datetime.now().time()
    print(f'Time: {cur_time.strftime(custom_format)}')

    if local_dict != remote_dict:
        write(remote_dict)
        return convert_to_string(changed_dict)
    else:
        return ''

def get_custom_currency(rates:str='') -> str:
    rates = rates.replace(" ", "").strip().upper().split(",")

    remote_dict = download_rates()
    local_dict = read()
    changed_dict = check_changes(local_dict, remote_dict)
    if len(changed_dict) != 0:
        write(remote_dict)
    message = {}
    for rate in rates:
        if rate in remote_dict:
            message[rate] = remote_dict[rate]

    message = convert_to_string(message)

    if len(changed_dict) != 0:
        for rate in message:
            if rate in changed_dict:
                del changed_dict[rate]
        if len(message) == 0:
            message = 'No currency found.'
        changed_dict = f"Also changed:\n{convert_to_string(changed_dict)}"
        message = message + '\n\n'+ changed_dict

    return message

def get_all_currencies() -> str:
    changed_dict = check_changes()
    local_dict = read()

    if len(changed_dict) != 0:
        if len(changed_dict) != 0:
            for rate in  changed_dict:
                if rate in local_dict:
                    del local_dict[rate]
        changed_dict = f'\n\nChanged:\n{convert_to_string(changed_dict)}'
    result = convert_to_string(local_dict)
    result = f'{result}{changed_dict if len(changed_dict) != 0 else ""}'
    return result