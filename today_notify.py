from distribute import send_discord
RESERVATION_FILE_PATH = "reservations.json"
from datetime import datetime
import json
import configparser
import telebot
from formatting import convert_to_human_day, format_reservation



config = configparser.ConfigParser()
config.read('config.ini')
def parse_time(time_str):
    """Parses a time string like "11:00am" into a datetime.time object."""
    return datetime.strptime(time_str, "%I:%M%p").time()

def sort_by_start_time(meetings):
    """Sorts a list of reserve by their start time."""
    return sorted(meetings, key=lambda meeting: parse_time(meeting["start_time"]))



#Notify about any reservations on current date.
today_obj = datetime.today()
with open(RESERVATION_FILE_PATH, 'r') as f:
    week_reservations = json.load(f)

day_key_str = today_obj.strftime("%Y-%m-%d")
reservations_for_today = week_reservations.get(day_key_str)

# Send it if there was one from last week (use today's date)
print(f'[Found {str(reservations_for_today)}]')
if reservations_for_today:
    if reservations_for_today == "LIB_CLOSED":
        output_today = f'Library Closed Today {convert_to_human_day(today_obj)}'
    else:
        #reservations_for_today = sort_by_start_time(reservations_for_today)
        output_today = f'Reservations for Today\n\n{convert_to_human_day(today_obj)}'
        for res in reservations_for_today:
            if res['confirmed']:
                output_today + "\n"
                output_today += format_reservation(res, hide_confirmed=True)
                output_today + f"\n"
else:
    output_today = 'None found, check main output from last week :('

# Output today's reservation for the squad
bot = telebot.TeleBot(config['TELEGRAM']['token'])
bot.send_message(config['TELEGRAM']['roomID'], output_today)
send_discord(output_today, config['DISCORD']['webhookToday'])
print(f'[Today\'s distribution complete]\n')
print(output_today)