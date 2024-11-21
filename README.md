# RoomBotUCF2.0

UCF Library Study Room Reservation Bot v2.0 – A Python bot to quickly reserve UCF Library study rooms using the Unofficial LibCal API, no Selenium or browser



This project is the successor to [RoomBotUCF 1.0](https://github.com/thefrostedfrakes/RoomBotUCF), which used Selenium and was slow and inefficient as a result. This project aims to address those issues and provide a more efficient solution.

## Components

#### Login Checker
`check_logins.py`, checks the accounts/logins before reservations each night, sets them invalid if it fails to login. This should be run for example like at 11:30PM

#### RoomBot
`__main__.py` This is the actual room bot that will reserve the rooms, it should be launched at like 11:58PM, it will wait exactly till 11:59PM to run it's self. It will reserve the rooms for the day a week ahead.
#### Django Web Page
`roombot_web_project` Django Website for displaying reservations, as well as pages for updating invalid credentials or adding users/logins for the bot to use.
#### Today Notify
`today_notify.py` Notifies of reservations for the current day on Discord and Telegram.


## JSON Files

#### reservations.json
Stores the details of all the reservations made by the bot, including room numbers, times, and user information.

#### logins.json
Contains the login credentials for the users that the bot will use to make reservations. This file is checked by `check_logins.py` to ensure all credentials are valid.

#### locked_nicknames.json
This JSON allows setting a nickname to always use for one of the reserved rooms
```json
{"2": "Epic Study Room"}
```
This for example will cause the second study room to always be reserved under the nickname `Epic Study Room`

#### wanted_room_order.json
Specifies the preferred order of rooms that the bot should attempt to reserve, allowing users to prioritize certain rooms over others.
