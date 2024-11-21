import requests
from datetime import datetime, timedelta
from slots.add_time_slot import add_time_slot, update_add_slots
from extract_rooms import get_room_info
from grid import get_grid
from slots.createcart import create_cart
from checkout import libcal_checkout, print_checkout
import json
from libcal_exception import LibCalError, ExceedsDailyLimitError, TimesUnavailableError
from login.login import login
from distribute import  send_discord
from formatting import format_reservation, convert_to_human_day
from response_str import print_response_str
from wait_until import wait_until
import traceback
import configparser
import os
import random
from nick_gen import generate_codename
from library_hours import LibCalSchedule
from filepaths import LOGIN_JSON_PATH

config = configparser.ConfigParser()
config.read('config.ini')
DEBUG = True
DEBUG_FOLDER = "debug"
DEBUG_LOGIN = False
USE_NICKGEN = True
BASE_URL = "https://ucf.libcal.com"
# Gets static room info /ids / room numbers from javascript inside html
rooms = get_room_info()
if DEBUG:
    # Write the extracted JavaScript code JSON to a JSON file
    with open(os.path.join(DEBUG_FOLDER, 'extracted_rooms_spaces.json'), 'w', encoding='utf-8') as json_file:
        json.dump(rooms, json_file, indent=4)
wanted_room_info = None

#Load locked nicknames
with open('locked_nicknames.json', 'r') as file:
    locked_nicknames = json.load(file)

# Load UCF login info from JSON file
with open(LOGIN_JSON_PATH, 'r') as file:
    login_info = json.load(file)

accounts_valid_count = 0
valid_accounts = []
for account in login_info:
    if account['validCredentials']:
        accounts_valid_count += 1
        valid_accounts.append(account)

random.shuffle(valid_accounts)

#4 hours per account, 30 min slots = 8 slots per account
time_slots_capable_for_day = accounts_valid_count * 7
hours_capable_for_day = time_slots_capable_for_day/2
print(f"Accounts valid #: {accounts_valid_count}, Time slots capable for day: {time_slots_capable_for_day}, Total hours: {time_slots_capable_for_day/2}")


# Load list of just room/numbers in order wanted
with open('wanted_room_order.json', 'r') as file:
    wanted_room_order = json.load(file)


#Combine with actual room info (spaces)
wanted_room_info_list = []
for room_number in wanted_room_order:
    for room_idx, room_info in rooms.items():
        if room_info['extracted_room_number'] == room_number:
            wanted_room_info_list.append(room_info)


# Get the current date
current_date = datetime.now().date()

# Get x days ahead
reserve_day_dt = current_date + timedelta(days=8)
day_after_reserve_day_dt = reserve_day_dt + timedelta(days=1)

# Format the dates as strings
reserve_day = reserve_day_dt.strftime("%Y-%m-%d")

day_after_reserve_day = day_after_reserve_day_dt.strftime("%Y-%m-%d")

#Assuming 7:30AM to 1AM next day
# Calculate the room count based on the hours


day_status = LibCalSchedule.get_status_for_date(reserve_day_dt)

#ASSUMING
hours_open = day_status.hours_open_total()
slots_for_whole_day= hours_open * 2
room_count = int(hours_capable_for_day // 17.5) + 1


print(f"Room count: {room_count}")
msg = f"""
HRS Open {hours_open}
Room Count: {room_count}
Slots to fill entire room req. {slots_for_whole_day}
Valid Accounts: {len(valid_accounts)}
"""
send_discord(msg, config['DISCORD']['webhookMain'])


#ALLOCATES WHAT USERS TO USE FOR WHAT ROOMS AND SLOTS
selected_rooms_list = wanted_room_info_list[:room_count]
MAX_SLOTS_PER_USER_PER_DAY = 8 # 8 30 min slots/ 4 hours
user_i = 0
for user in valid_accounts:
    user['slots_to_reserve'] = [0 for _ in range(room_count)]
full_user = valid_accounts[user_i]
user = full_user
user['assumed_used_slots'] = 0

for room_idx, room in enumerate(selected_rooms_list):
    #Init reservers
    if 'reservers' not in room:
        room['reservers'] = []
    slot_position_i = 0
    while slot_position_i < slots_for_whole_day:
        #Switch to next user ran out
        if user['assumed_used_slots'] >= MAX_SLOTS_PER_USER_PER_DAY:
            user_i += 1
            #Max users reached, all alcocated
            if user_i >= len(valid_accounts):
                break
            full_user = valid_accounts[user_i]
            user = full_user
            user['assumed_used_slots'] = 0

        #Fills a slot
        slots_left_to_fill_in_room = slots_for_whole_day - slot_position_i
        user_amount_left = MAX_SLOTS_PER_USER_PER_DAY - user['assumed_used_slots']
        if slots_left_to_fill_in_room >= user_amount_left:
            slots_to_reserve = user_amount_left
        else:
            slots_to_reserve = slots_left_to_fill_in_room
        #SLOTS should Always be a whole number
        slots_to_reserve = int(slots_to_reserve)
        user["slots_to_reserve"][room_idx] = slots_to_reserve
        user['assumed_used_slots'] += slots_to_reserve
        room['reservers'].append(user)
        slot_position_i += slots_to_reserve
        #This room is done
        if slots_left_to_fill_in_room == 0:
            break

# Export selected_rooms_list to a JSON file
if DEBUG:
    with open(os.path.join(DEBUG_FOLDER, 'selected_rooms_list.json'), 'w', encoding='utf-8') as json_file:
        json.dump(selected_rooms_list, json_file, indent=4)


#LIBRARY ID LID UCF IS 2824
lid = 2824
#Group ID is set of rooms regular or large, 4779 or 4780 or 0 is all
gid = 0
#WAIT FOR GRID TO BE AVAILABLE
#Example usage: wait until 11:59 PM today (local timezone)

# 10 secondnsnsns
target_time = datetime.now().replace(hour=23, minute=59, second=4, microsecond=0)
print("Plan is ")
for room_idx, room in enumerate(selected_rooms_list):
    print(f"\tRoom {room_idx} {room['title']} {room['extracted_room_number']}")
    for reserver in room['reservers']:
        print(f"\t\tReserver {reserver['name']} planned slots for this room {reserver['slots_to_reserve'][room_idx]}")
print("Reserve for day is", reserve_day)
wait_until(target_time)

try:
    #EID is the actual room id, -1 for all
    eid = -1
    grid = get_grid(lid, gid, reserve_day, day_after_reserve_day, eid)


    print(f"Grid response {grid.status_code}")
    grid.raise_for_status()
    #print(grid.text)
    grid = grid.json()

    # Index the grid slots by itemId/EID room ID
    idx_grid = {}
    for idx, slot in enumerate(grid['slots']):
        if slot['itemId'] not in idx_grid.keys():
            idx_grid[slot['itemId']] = [slot]
        else:
            idx_grid[slot['itemId']].append(slot)
    if DEBUG:
        # Write grid to JSON FILE
        with open(os.path.join(DEBUG_FOLDER, 'grid.json'), 'w', encoding='utf-8') as json_file:
            json.dump(rooms, json_file, indent=4)

    if not grid['slots']:
        print("No slots available")
        raise LibCalError("No slots available for "+reserve_day)


    i = 0
    earliest_start = "07:00:00"
    earliest_start = datetime.strptime(earliest_start, "%H:%M:%S").time()
    reservations = []
    for room_idx, room in enumerate(selected_rooms_list):
        room_complete_for_day = False
        print(f"Room {room_idx} {room['title']} {room['extracted_room_number']} - {room['eid']}")
        if room['eid'] not in idx_grid.keys():
            raise LibCalError("Room not found in grid, no slots")
        #Iterates slots for only the current room
        room_reserver_idx = 0
        room_slot_idx = 0
        #First slot
        slot = idx_grid[room['eid']][room_slot_idx]
        #Iterate slots for the room, until all slots are filled, and reservers still avaliable
        while room_slot_idx < len(idx_grid[room['eid']]) and room_reserver_idx < len(room['reservers']):
            reserver = room['reservers'][room_reserver_idx]
            print(f"Reserver {reserver['name']} planned slots for this room {reserver['slots_to_reserve'][room_idx]}")
            reservation = {"room": room['extracted_room_number'], "session": requests.Session(), 'reserver': reserver, 'confirmed': False, 'state': "init"}
            reservations.append(reservation)
            session = reservation["session"]
            slot = idx_grid[room['eid']][room_slot_idx]
            #Iterates idx until slot is available and late enough of wanted start time
            while room_slot_idx+1 < len(idx_grid[room['eid']]) and (datetime.strptime(slot['start'], "%Y-%m-%d %H:%M:%S").time() < earliest_start or slot.get("className") == "s-lc-eq-checkout"):
                #Slot taken, move to next
                room_slot_idx += 1
                taken = slot.get("className") == "s-lc-eq-checkout"
                print(("Taken" if taken else "slot too early")+" moving to next", "Skipped", "Slot start", slot['start'])
                slot = idx_grid[room['eid']][room_slot_idx]
            #LAST ONE AND FULL BREAK
            if room_slot_idx+1 >= len(idx_grid[room['eid']]) and  slot.get("className") == "s-lc-eq-checkout":
                print(f"{room['extracted_room_number']} Room is full/taken no slots, complete for day")
                reservation['error'] = "Room is full/taken no slots, complete for day"
                break
            room_info = {
                "eid": room['eid'],
                "gid": room['gid'],
                "lid": room['lid'],
                "start": slot['start'],
                "checksum": slot['checksum'],
                "end": slot['end']
            }

            add_rsp = add_time_slot(session, room_info)
            reservation['state'] = "add_complete"
            #An inital add, will return updated, that checksum is required to make a booking longer than 1 slot
            print(f"\nAdd response {add_rsp.status_code} ------------------------------")
            add_rsp.raise_for_status()
            if add_rsp.status_code == 200 and "unavailable" in add_rsp.text:
                raise TimesUnavailableError()
            add_info = add_rsp.json()
            bookings = add_info['bookings']
            print("Response for this Booking returned options, start time was", room_info['start'])
            for idx, option in enumerate(bookings[0]['options']):
                print(f"Option {idx} {option}")

            booking_checksum = bookings[0]['checksum']

            selected_option_idx = reserver['slots_to_reserve'][room_idx]-1
            if selected_option_idx >= len(bookings[0]['options']):
                selected_option_idx = -1
            selected_end = bookings[0]['options'][selected_option_idx]
            selected_checksum = bookings[0]['optionChecksums'][selected_option_idx]
            room_info['update_end'] = selected_end
            rsp = update_add_slots(session, room_info, selected_checksum, booking_checksum)
            reservation['state'] = "update_add_complete"
            room_info['end'] = selected_end
            room_info['checksum'] = booking_checksum
            print(rsp.status_code)
            rsp.raise_for_status()
            rsp_json = rsp.json()
            booking = rsp_json["bookings"][0]
            booking['UCFID'] = reserver['UCFID']
            booking['room'] = room['extracted_room_number']
            booking['name'] = reserver['name']
            reservation.update(booking)
            room_info['end'] = booking['end']
            room_info['checksum'] = booking['checksum']

            cart_rsp = create_cart(session, room_info)
            #print(f"Cart response {cart_rsp.status_code},")
            print("Cart Response ------------------------------")
            try:
                cart_rsp.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print("Cart response failed", cart_rsp.text)
                raise e
            if DEBUG:
                print_response_str(cart_rsp)
            cart_rsp_dict = cart_rsp.json()
            reservation['state'] = "cart_complete"
            #Move on to next reserver
            room_reserver_idx += 1
            #Move to next slot however far, for next iter
            room_slot_idx += reserver['slots_to_reserve'][room_idx]



    for reservation in reservations:
        if not reservation.get("error"):
            session = reservation['session']
            reserver = reservation['reserver']
            reservation['state'] = "attempting_login"

            #ADD CHECK LOGIN BAD HANDLE, shouldn't really happen since we pre check but anyway
            try:
                info = login(cart_rsp_dict, session, reserver['NID'], reserver['password'], DEBUG_LOGIN)
            except Exception:
                reservation['error'] = "login_failed"
            else:
                reservation['state'] = "logged_in"

                # Print in a readable format
                print("Logged in returned info")
                print("Logged in as", info['logged_in_as'])
                print(f"Room Name: {info['room_name']}")
                print(f"Location: {info['location']}")
                print(f"Start Time: {info['start_time']}")
                print(f"End Time: {info['end_time']}")
                session_id = info['session_id']

                #checkout final
                room_order_number = wanted_room_order.index(reservation['room'])+1

                #Firstly Locked nickname to one of the rooms
                if locked_nicknames.get(str(room_order_number)):
                    nickname = locked_nicknames.get(str(room_order_number))
                #Second Random nicks, if enabled
                elif USE_NICKGEN:
                    nickname = generate_codename(reserver['name'])
                # Third User Nicks 
                elif reserver['nickname']:
                    nickname = reserver['nickname']
                else: 
                    nickname = None

                if nickname:
                    reservation['nickname'] = nickname
                else:
                    nickname = reserver['name']


                student_type = "Undergraduate Student"
                last_name = reserver['name'].split(" ")[-1]
                eid = reservation['eid']
                checkout_rsp = libcal_checkout(session, nickname, reserver['UCFID'], student_type, session_id, last_name, eid)
                print("Checkout rsp", checkout_rsp.status_code)
                reservation['state'] = "checkout_complete"
                if checkout_rsp.status_code == 500 and "exceeds the" in checkout_rsp.text:
                    print("Exceeds daily limit")
                    reservation['error'] = "Exceeds daily limit"
                    #raise ExceedsDailyLimitError()
                else:
                    checkout_rsp.raise_for_status()

                    reservation['confirmed'] = True
                print_checkout(checkout_rsp.text)
            finally:
            # Close out the requests session
                session.close()
                reservation.pop("session")



except Exception as e:
    print("Error encountered", e)
    print(traceback.format_exc())
    send_discord(str(e), config['DISCORD']['webhookMain'])

#Clean up session and unwanted keys in reservation
REMOVE_KEYS = ["id", "eid", "seat_id", "gid", "lid", "cost", "optionChecksums", "options", "checksum", "seat_id"]
for reservation in reservations:
    for key in REMOVE_KEYS:
        if reservation.get(key):
            reservation.pop(key)
    if reservation.get("session"):
        session = reservation["session"]
        session.close()
        reservation.pop("session")
    #Only remove password, if it exists, but it should always be in reserver at this point but isn't ?!?!
    if reservation.get("reserver") and reservation['reserver'].get('password'):
        reservation['reserver'].pop("password")




msg = f"Reservations for {convert_to_human_day(reserve_day_dt)}\n"
send_discord(msg, config['DISCORD']['webhookMain'])
print(reserve_day_dt)
for reservation in reservations:

    msg = f"\n```{format_reservation(reservation)}```\n"

    # Send the reservation information to the Discord webhook
    send_discord(msg, config['DISCORD']['webhookMain'])



#  Load the JSON file
with open('reservations.json', 'r') as file:
    data = json.load(file)


data[reserve_day] = reservations

#  Save the modified JSON back to the file
with open('reservations.json', 'w') as file:
    json.dump(data, file, indent=4)  