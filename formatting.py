'''
Auxiliary file with functions to help manage information about the rooms

Jack Sweeney
11.12.2024
'''

from datetime import datetime, timedelta, time

def convert_to_human_day(input_datetime):
    day = datetime.strftime(input_datetime, '%d').lstrip('0')
    day_string = input_datetime.strftime(f'%A, %B {day}, %Y')
    return day_string

def convert_to_12hr_format(date_str):
    # Parse the input date string
    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    # Format it to the 12-hour time with AM/PM
    return date_obj.strftime("%I:%M %p").lstrip("0").lower()


def format_reservation(reservation_dict, hide_confirmed=False):
    reserver = reservation_dict.get("reserver")
    if reservation_dict.get("confirmed"):
        room_info = f'''{reservation_dict["room"]} | {convert_to_12hr_format(reservation_dict["start"])} - {convert_to_12hr_format(reservation_dict["end"])}'''
    else:
        room_info = f"Wanted room was {reservation_dict['room']}"

    if reservation_dict.get("nickname"):
        nick_str = f" as {reservation_dict['nickname']}"
    else:
        nick_str = ""




    out =  f'''\t
        • {room_info}
    \t\t\tUnder: {reserver['name']}{nick_str}
        
    '''
    if not hide_confirmed:
        out += f"\n\tConfirmed: {reservation_dict['confirmed']}"
    if reservation_dict.get("error"):
        out += f"\n\tState: {reservation_dict['state']}\n\tError: {reservation_dict['error']}"

    return out

