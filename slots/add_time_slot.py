import requests

def add_time_slot(session, room_info):

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
        'add[eid]': str(room_info['eid']),
        'add[gid]': str(room_info['gid']),
        'add[lid]': str(room_info['lid']),
        'add[start]': room_info['start'],
        'add[checksum]': str(room_info['checksum']),
        'lid': str(room_info['lid']),
        'gid': str(room_info['gid']),
        'start': room_info['start'].split(" ")[0],
        'end': room_info['end'].split(" ")[0],
    }

    response = session.post('https://ucf.libcal.com/spaces/availability/booking/add', headers=headers, data=data)
    return response


def update_add_slots(session, room_info, add_checksum, booking_checksum):
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://ucf.libcal.com',
        'priority': 'u=1, i',
        'referer': 'https://ucf.libcal.com/spaces?lid=2824&gid=4779&c=0',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'update[id]': '1',
        'update[checksum]': add_checksum, #
        'update[end]': room_info['update_end'],
        'lid': str(room_info['lid']),
        'gid': str(room_info['gid']),
        'start': room_info['start'].split(" ")[0],
        'end': room_info['start'].split(" ")[0],
        'bookings[0][id]': '1',
        'bookings[0][eid]': str(room_info['eid']),
        'bookings[0][seat_id]': '0',
        'bookings[0][gid]': str(room_info['gid']),
        'bookings[0][lid]': str(room_info['lid']),
        'bookings[0][start]': room_info['start'],
        'bookings[0][end]': room_info['end'],
        'bookings[0][checksum]': booking_checksum, #This is the booking checksum from the last response
    }

    response = session.post('https://ucf.libcal.com/spaces/availability/booking/add', headers=headers, data=data)
    return response