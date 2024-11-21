import requests
from datetime import datetime, date, timedelta

#UCF LIBCAL SPECS
IID = 246
LID = 1206
class LibCalResponseError(Exception):
    """Custom exception class for LibCal errors."""
    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception

    def __str__(self):
        if self.original_exception:
            return f"{self.message} (caused by {self.original_exception})"
        return self.message

class LibCalSchedule:
    @staticmethod
    def get_json_data_for_date(date: date) -> dict:
                                #Date looks like 2024-07-07
        formatted_date = date.strftime("%Y-%m-%d")
        url = f"https://api3.libcal.com/api_hours_grid.php?format=json&weeks=1&iid={IID}&lid={LID}&date={formatted_date}&format=json"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            json_data = response.json()
        except requests.HTTPError as http_err:
            raise LibCalResponseError("HTTP error occurred", http_err)
        except requests.ConnectionError as conn_err:
            raise LibCalResponseError("Connection error occurred", conn_err)
        except requests.Timeout as timeout_err:
            raise LibCalResponseError("Timeout error occurred", timeout_err)
        except requests.RequestException as req_err:
            raise LibCalResponseError("An error occurred during the request", req_err)
        except ValueError as json_err:
            raise LibCalResponseError("JSON decode error occurred", json_err)
        return json_data

    @staticmethod
    def select_lid(json_data: dict, lid: int) -> dict:
        for loc_key, loc_data in json_data.items():
            if loc_key == f"loc_{lid}":
                return loc_data
        return None
    @staticmethod
    def select_day_in_week(week: dict, day: date) -> dict:
        for day_key, day_data in week.items():
            if day_data['date'] == day.strftime("%Y-%m-%d"):
                day_data['day'] = day_key
                return day_data
        return None


    @staticmethod
    def get_status_for_date(date: date) -> dict:
        json_data = LibCalSchedule.get_json_data_for_date(date)
        loc_data = LibCalSchedule.select_lid(json_data, LID)
        week = loc_data["weeks"][0]
        selected_day_data = LibCalSchedule.select_day_in_week(week, date)
        return DayStatus(selected_day_data)

class HoursBlock:
    def __init__(self, hours_block: dict, current_date: date):
        if ":" in hours_block['from']:
            from_time = datetime.strptime(hours_block['from'], "%I:%M%p").time()
        else:
            from_time = datetime.strptime(hours_block['from'], "%I%p").time()
        self.from_time = datetime.combine(current_date, from_time)

        if ":" in hours_block['to']:
            to_time = datetime.strptime(hours_block['to'], "%I:%M%p").time()
        else:
            to_time = datetime.strptime(hours_block['to'], "%I%p").time()

        to_time_day = current_date if to_time > from_time else (current_date + timedelta(days=1))
        self.to_time = datetime.combine(to_time_day, to_time)



class DayStatus:
    def __init__(self, data: dict):
        self.date = datetime.strptime(data['date'], "%Y-%m-%d").date()
        self.status = data['times']['status']
        self.hours = []
        if self.status != "closed":
            for hours_block in data['times']['hours']:
                self.hours.append(HoursBlock(hours_block, self.date))
        self.currently_open = data['times']['currently_open']
        self.rendered = data['rendered']
    def __str__(self):
        return (f"DayStatus object at {hex(id(self))}\n"
                f"date: {self.date}\n"
                f"status: {self.status}\n"
                f"hours: {self.hours}\n"
                f"currently_open: {self.currently_open}\n"
                f"rendered: {self.rendered}")
    def hours_open_total(self):
        hours_count = 0
        for block in self.hours:
            time_difference = block.to_time - block.from_time
            hours_difference = time_difference.total_seconds() / 3600
            hours_count += hours_difference
        return hours_count


