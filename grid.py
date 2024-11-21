import requests
def get_grid(lid, gid, start, end, eid=-1):
    headers = {
        'authority': 'ucf.libcal.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://ucf.libcal.com',
        'pragma': 'no-cache',
        'referer': 'https://ucf.libcal.com/reserve/generalstudyroom',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'lid': str(lid),
        'gid': str(gid),
        'eid': str(eid),
        'seat': '0',
        'seatId': '0',
        'zone': '0',
        'start': start,
        'end': end,
        'pageIndex': '0',
        'pageSize': '18',
    }

    response = requests.post('https://ucf.libcal.com/spaces/availability/grid', headers=headers, data=data)

    return response