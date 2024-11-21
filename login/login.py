from login.authenticate import saml_authenticate_php
from req_headers import headers
from login.saml1 import saml_login
from login.springysp import springy_sp
from login.saml2 import saml_get
from bs4 import BeautifulSoup
import re
import urllib.parse
import os
from response_str import print_response_str
DEBUG_HTML_FOLDER = "debug_html"
BASE_URL = "https://ucf.libcal.com"
def login(cart_rsp_dict, session, username, password, debug=False):


    #Reservation is now setup with system we know must login, the cart response gave a url to redirect to login for auth
    # Auth Step 1 includes 3 redirects, https://ucf.libcal.com/spaces/auth?returnUrl > https://libauth.com/linker?app= >
    # https://libauth.com/saml/module.php/core/authenticate.php?as=springy-sp
    params = {
        'returnUrl': '/reserve/generalstudyroom',
    }
    url = BASE_URL+cart_rsp_dict['redirect']
    if debug:
        print(url)
    session.max_redirects = 8
    redir_auth_rsp = session.get(url, allow_redirects=True, params=params, headers=headers)
    if debug:
        print("Redir Auth ------------------------------")

    if redir_auth_rsp.history:
        if debug:
            print("Redirected!")
            print("Final URL:", redir_auth_rsp.url)
            print("Final Status Code:", redir_auth_rsp.status_code)

        # Print information about each step in the redirection history
        for idx, redirect_response in enumerate(redir_auth_rsp.history, 1):
            if debug:
                print(f"Step {idx} - URL: {redirect_response.url}, Status Code: {redirect_response.status_code}")
            if idx == 2: # Request 2 has the site rid https://libauth.com/linker?app= or check for https://libauth.com/linker?app=
                rid = redirect_response.cookies['rid']
                if debug:
                    print(f"RID is: {rid}")
    else:
        if debug:
            print("Not Redirected!")
            print("Status Code:", redir_auth_rsp.status_code)
    # disco_1_rsp = session.get(redir_auth_rsp.url, allow_redirects=True, headers=headers)
    # print(f"Disco1 response {disco_1_rsp.status_code}")
    disco2_with_rid_url = redir_auth_rsp.url + f"&idpentityid={rid}"
    #print(disco2_with_rid_url)
    disco2_auth_rsp = session.get(disco2_with_rid_url, allow_redirects=True, headers=headers)
    if debug:
        print("Disco auth rsp ------------------------------")
        print_response_str(disco2_auth_rsp)
        print(disco2_auth_rsp.headers)
    inital_saml_referer = disco2_auth_rsp.url
    saml_get_rsp1 = saml_get(session, inital_saml_referer, "https://libauth.com/")
    if debug:
        print("SAML Login GET RSP 1  -----------")

        with open(os.path.join(DEBUG_HTML_FOLDER, "saml_get_rsp1.html"), "w") as text_file:
            text_file.write(saml_get_rsp1.text)

    # Create a BeautifulSoup object
    soup = BeautifulSoup(saml_get_rsp1.text, 'html.parser')

    # Find the form with id 'loginForm'
    login_form = soup.find('form', {'id': 'loginFormPaginated'})

    # Extract the value of the 'action' attribute
    if login_form:
        action_value = login_form.get('action')
        print("Action Value:", action_value)
    else:
        print("Login form not found.")
    new_saml_url = f"https://federation.net.ucf.edu{action_value}"
    username = f"{username}@ucf.edu"
    saml_rsp = saml_login(session, username, password, new_saml_url, inital_saml_referer)
    if debug:
        print("SAML Login POST RSP -----------")
        print(saml_rsp.status_code, saml_rsp.url)

    saml_get_rsp2 = saml_get(session, new_saml_url, inital_saml_referer)
    if debug:
        print("SAML Login GET RSP 2 -----------")
        with open(os.path.join(DEBUG_HTML_FOLDER, "saml_get_rsp2.html"), "w") as text_file:
            text_file.write(saml_get_rsp2.text)
        print_response_str(saml_get_rsp2)
    # Parse the HTML content
    soup = BeautifulSoup(saml_get_rsp2.text, 'html.parser')

    # Find the form element by name
    form = soup.find('form', {'name': 'hiddenform'})

    # Find the input elements within the form
    saml_response_input = form.find('input', {'name': 'SAMLResponse'})
    relay_state_input = form.find('input', {'name': 'RelayState'})

    # Extract the values
    saml_response_value = saml_response_input['value'] if saml_response_input else None
    relay_state_value = relay_state_input['value'] if relay_state_input else None


    springy_response = springy_sp(session, saml_response_value, relay_state_value)
    if debug:
        print("Springy POST RSP -----------", springy_response.status_code)
        print(springy_response.url)
        with open(os.path.join(DEBUG_HTML_FOLDER, "springy.html"), "w", encoding="utf-8") as text_file:
            text_file.write(springy_response.text)

    html_content = springy_response.text
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the link with the class 's-lc-session-aware-link'
    link = soup.find('a', class_='s-lc-session-aware-link')

    # Extract the href attribute
    href = link.get('href')

    # Extract the session ID from the href attribute
    if href and 'session=' in href:
        session_id = href.split('session=')[1]
        print(f'Session ID: {session_id}')

    # Find the <a> tag with the specific class
    link = soup.find('a', class_='s-lc-session-aware-link')

    # Get the text and strip unnecessary whitespace, then split off "- Logout"
    logged_in_user = link.text.strip().split(" - ")[0]


    # Extracting the data
    room_name = soup.find('strong').get_text(strip=True)
    location = soup.find_all('td')[2].get_text(strip=True)
    start_time = soup.find_all('td')[3].get_text(strip=True)
    end_time = soup.find_all('td')[4].get_text(strip=True)




    info = {"logged_in_as": logged_in_user, "room_name": room_name, "location": location, "start_time": start_time, "end_time": end_time, "session_id": session_id}
    return info
