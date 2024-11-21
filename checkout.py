import requests
from bs4 import BeautifulSoup
import html
def libcal_checkout(session, nick, student_id, student_type, session_id, last_name, space_id):



    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'origin': 'https://ucf.libcal.com',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': f'https://ucf.libcal.com/spaces/auth?returnUrl=%2Fspace%2F{space_id}',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }

    files = {
        'nick': (None, nick),
        'q2613': (None, student_type),
        'q2614': (None, student_id),
        'returnUrl': (None, f'/space/{space_id}'),
        'logoutUrl': (None, 'logout'),
        'session': (None, session_id),
    }


    response = session.post('https://ucf.libcal.com/ajax/equipment/checkout', headers=headers, files=files)

    return response

def print_section(title, dt_dd_pairs):
    print(f"\n{title}")
    print("-" * len(title))
    for dt, dd in dt_dd_pairs:
        print(f"{dt}: {dd}")
    print()  # Blank line for separation between sections

def print_checkout(checkout_html):
# Print the parsed and formatted information
    # Parse the HTML with html.parser
    # Step 1: Convert the Unicode escapes to HTML
    decoded_html = bytes(checkout_html, "utf-8").decode("unicode_escape")
    soup = BeautifulSoup(decoded_html, 'html.parser')


    # Extract the booking confirmation section
    confirmation = soup.find('h1', class_='s-lc-eq-success-title').text.strip()
    print(f"{confirmation}\n")

    # Extract email confirmation paragraph
    email_confirmation = soup.find('p').text.strip()
    print(f"{email_confirmation}\n")

    # Extract the Space Information section
    space_info_title = soup.find('div', class_='s-lc-eq-success-resource').h2.text.strip()
    space_info_items = [(dt.text.strip(), dt.find_next_sibling('dd').text.strip())
                        for dt in soup.find('div', class_='s-lc-eq-success-resource').find_all('dt')]

    print_section(space_info_title, space_info_items)

    # Extract the User Information section
    user_info_title = soup.find('div', class_='s-lc-eq-success-user').h2.text.strip()
    user_info_items = [(dt.text.strip(), dt.find_next_sibling('dd').text.strip())
                        for dt in soup.find('div', class_='s-lc-eq-success-user').find_all('dt')]

    print_section(user_info_title, user_info_items)