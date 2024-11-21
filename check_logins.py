import json
from epc_check_login import check_login
from filepaths import LOGIN_JSON_PATH
import time
import random
from datetime import datetime, timedelta
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')
from distribute import send_discord
def main():
    valid_count = 0
    invalid_count = 0
    with open(LOGIN_JSON_PATH, 'r') as f:  # 'r+' for read and write access
        logins = json.load(f)

    for login in logins:
        if login.get('updated'):
            #Updated like date 11/8/2024
            #Check if updated in last 3 days
            updated = datetime.strptime(login['updated'], "%m/%d/%Y").date()
            recent = updated > datetime.now().date() - timedelta(days=3)
            if recent:
                print(f"Login for {login['name']} was updated recently on {login['updated']}")
        else:
            recent = False
        if login['validCredentials'] or recent:
            print(f"Checking login for {login['name']}")
            validCredential = check_login(login['NID'], login['password'])
            print(f"Valid: {validCredential}\n")
            if validCredential:
                valid_count += 1
            else:
                invalid_count += 1
                send_discord(f"Invalid login for {login['name']}", config['DISCORD']['webhookLogins'])

            login['validCredentials'] = validCredential  # Update validCredentials
            time.sleep(random.randint(4, 18))  # Sleep for x second to avoid rate limiting, if any and randomize
        else:
            print(f"Skipping login for {login['name']} already set to false")
            invalid_count += 1

    with open(LOGIN_JSON_PATH, 'w') as f:
        # Write the updated data back to the file
        json.dump(logins, f, indent=4)

        # Truncate any remaining data in the file
        f.truncate()

    print("Login information updated.")
    print(f"Valid logins: {valid_count}")
    print(f"Invalid logins: {invalid_count}")
    print("Total logins:", valid_count + invalid_count)

if __name__ == "__main__":
    main()