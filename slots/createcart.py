import requests
import json
def create_cart(session, room_info):
    headers = {
        'authority': 'ucf.libcal.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://ucf.libcal.com',
        'pragma': 'no-cache',
        'referer': 'https://ucf.libcal.com/reserve/generalstudyroom',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'libAuth': 'true',
        'blowAwayCart': 'true',
        'returnUrl': '/reserve/generalstudyroom',
        'bookings[0][id]': '1',
        'bookings[0][eid]': str(room_info['eid']),
        'bookings[0][seat_id]': '0',
        'bookings[0][gid]': str(room_info['gid']),
        'bookings[0][lid]': str(room_info['lid']),
        'bookings[0][start]': room_info['start'], #Like '2023-11-13 20:30'
        'bookings[0][end]': room_info['end'], # Like '2023-11-13 21:00'
        'bookings[0][checksum]': room_info['checksum'],
        'method': '11',
    }
    print(json.dumps(data, indent=2))
    response = session.post('https://ucf.libcal.com/ajax/space/times', headers=headers, data=data)
    return response