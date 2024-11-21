import json
from datetime import datetime
from django.shortcuts import render
from pathlib import Path
from django.utils import timezone
from django.http import JsonResponse

from datetime import datetime, timedelta
LOGIN_JSON_PATH = Path(__file__).resolve().parent.parent.parent / 'logins.json'
def format_time(dt):
    """Format time to be without leading zeros and with space before AM/PM."""
    return dt.strftime("%-I:%M %p")  # Use %-I for no leading zero

def calculate_end_time(meeting):
    # Parse the start time
    start_time_str = meeting['start_time']
    start_time = datetime.strptime(start_time_str, "%I:%M%p")

    # Convert duration from segments (30 minutes each) to minutes
    duration_minutes = meeting['duration'] * 30

    # Calculate the end time
    end_time = start_time + timedelta(minutes=duration_minutes)

    # Return the end time in desired format
    return end_time.strftime("%l:%M %p").strip()

def get_day_suffix(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        return "th"
    return ["st", "nd", "rd"][day % 10 - 1]


def get_reservations(request, date=None):
    if date:
        # Parse date string to a datetime object, if provided
        # Format datetime with custom suffix
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        date_word = date_obj.strftime("%A, %b %d") + get_day_suffix(date_obj.day)
        # Handle the date logic here
    else:
        date_obj = datetime.now()
        date_word = "Today"

    date_str = date_obj.strftime("%Y-%m-%d")
    # Load the JSON file from one level up
    LOGIN_JSON_PATH = Path(__file__).resolve().parent.parent.parent / 'reservations.json'

    # Open and load the JSON file
    with open(LOGIN_JSON_PATH, 'r') as f:
        data = json.load(f)



    # Retrieve reservations for the current date
    reservations = data.get(date_str, [])
    confirmed_reservations =  [r for r in reservations if r['confirmed']]

    for reservation in confirmed_reservations:
        if reservation['confirmed']:
            reservation['start'] = format_time(datetime.strptime(reservation['start'], "%Y-%m-%d %H:%M:%S"))
            reservation['end'] = format_time(datetime.strptime(reservation['end'], "%Y-%m-%d %H:%M:%S"))


    # Render the reservations in an HTML template
    return render(request, 'index.html', {'reservations': confirmed_reservations, 'date': date_str, 'date_word': date_word})



from django.shortcuts import render, redirect
from .models import Login
from django.contrib import messages

def update_credentials(request):

    # Load the JSON data
    with open(LOGIN_JSON_PATH, "r") as file:
        logins = json.load(file)

    # Filter invalid credentials
    invalid_users = [user for user in logins if not user.get("validCredentials")]

    if request.method == "POST":
        nid = request.POST.get("nid")
        ucfid = request.POST.get("ucfid")
        new_password = request.POST.get("password")

        # Find and update the user in the JSON data
        user_found = False
        for user in logins:
            if user["NID"] == nid:
                if ucfid != user["UCFID"]:
                    messages.error(request, "UCFID does not match user.")
                    return redirect("update_credentials")
                user["password"] = new_password
                user["validCredentials"] = True
                user["updated"] = datetime.now().strftime("%m/%d/%Y")
                user_found = True
                break

        if user_found:
            # Save the updated JSON data back to the file
            with open(LOGIN_JSON_PATH, "w") as file:
                json.dump(logins, file, indent=4)

            messages.success(request, f"Credentials updated for user {nid}.")
        else:
            messages.error(request, "User not found.")

        return redirect("update_credentials")

    return render(request, "update_credentials.html", {"invalid_users": invalid_users})

def add_user(request):
    

    # Load the JSON data
    with open(LOGIN_JSON_PATH, "r") as file:
        logins = json.load(file)

    if request.method == "POST":
        name = request.POST.get("name")
        nickname = request.POST.get("nickname")
        UCFID = request.POST.get("UCFID")
        NID = request.POST.get("NID")
        password = request.POST.get("password")

        # Check if the user already exists
        user_exists = any(user["NID"] == NID for user in logins)

        if user_exists:
            messages.error(request, f"User with NID {NID} already exists.")
        else:
            # Add new user to the list
            new_user = {
                "name": name,
                "nickname": nickname,
                "UCFID": UCFID,
                "NID": NID,
                "password": password,
                "validCredentials": True,
                "updated": datetime.now().strftime("%m/%d/%Y"),
            }
            logins.append(new_user)

            # Save the updated JSON data back to the file
            with open(LOGIN_JSON_PATH, "w") as file:
                json.dump(logins, file, indent=4)

            messages.success(request, f"User {name} has been added successfully.")
            return redirect("add_user")

    return render(request, "add_user.html")



def stats(request):
    try:
        # Load the logins.json file
        with open(LOGIN_JSON_PATH, 'r') as file:
            data = json.load(file)
        
        # Calculate counts
        valid_count = sum(1 for login in data if login.get("validCredentials", False))
        total_count = len(data)
        invalid_count = total_count - valid_count
        
        # Calculate hours
        hours = valid_count * 4
        
        # Pass data to the template
        context = {
            'valid_count': valid_count,
            'invalid_count': invalid_count,
            'total_count': total_count,
            'hours': hours
        }
        return render(request, 'stats.html', context)
    
    except FileNotFoundError:
        return JsonResponse({"error": "logins.json file not found"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Error parsing logins.json"}, status=400)
