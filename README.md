# RoomBotUCF2.0

UCF Library Study Room Reservation Bot v2.0 – A Python bot to quickly reserve UCF Library study rooms using the Unofficial LibCal API, no Selenium or browser

---

## Project Status

**Notice:**  
As of May 2025, further maintenance of this project is no longer worth it due to graduation and major changes in library authentication. This repository is now archived.  
**Message me if you have questions or need help, but please note that no updates or active support will be provided unless substantial interest or contributors appear.**

---

## Authentication Challenges

In the Winter of 2024, UCF changed how the Libcal sign in works with Microsoft/UCF SSO, requiring individual sessions and 2FA. At this point, the bot stopped working. Successfully logging in with requests for a system using SSO is the hardest part. This could only be solved by authenticating each user with 2FA and saving login session details, but the Microsoft session, cookies, and authentication workflow are extremely complex.

---

## Program History

See the full history and technical details here:  
**[RoomBotUCF – Historical background](https://gist.github.com/Jxck-S/091a8f98aa64bda5631a35c7400958c6)**

---

This project is the successor to [RoomBotUCF 1.0](https://github.com/thefrostedfrakes/RoomBotUCF), which used Selenium and was slow and inefficient as a result. This project aims to address those issues and provide a more efficient solution.

## Components

#### Login Checker
`check_logins.py`, checks the accounts/logins before reservations each night, sets them invalid if it fails to login. This should be run for example like at 11:30PM

#### RoomBot
`__main__.py` This is the actual room bot that will reserve the rooms. It should be launched at around 11:58PM; it will wait until exactly 11:59PM to run itself. At midnight, it will reserve rooms for the day exactly one week ahead.

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