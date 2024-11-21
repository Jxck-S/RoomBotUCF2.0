import requests
from bs4 import BeautifulSoup
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://www.cecs.ucf.edu',
    'Referer': 'https://www.cecs.ucf.edu/epc/login',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}
def check_login(username: str, password: str):
    """Checks a UCF Login, to verify if credentials are valid
    Args:
        username (str): The username to check (UCF NID)
        password (str): The password to check
    Returns:
        bool: True if the login is valid, False if the login is invalid
    """
    session = requests.Session()
    session.headers.update(headers)
    session.max_redirects = 6
    get_rsp_load = session.get("https://www.cecs.ucf.edu/epc/login")
    #print(get_rsp_load.status_code, get_rsp_load.url)


    # Parse the HTML
    soup = BeautifulSoup(get_rsp_load.text, 'html.parser')

    # Find the input element with the name "_token" and extract its value
    token = soup.find('input', {'name': '_token'}).get('value')

    #print("CSRF Token:", token)

    data = {
        '_token': token,
        'username': username,
        'password': password,
    }

    post_login_rsp = session.post('https://www.cecs.ucf.edu/epc/login', data=data)
    #print(post_login_rsp.status_code, post_login_rsp.url)


    #Checking response codes does not work, as the response code is always 200, redirects however and final url does.

    #BAD LOGIN
    if post_login_rsp.url == "https://www.cecs.ucf.edu/epc/login" or ("Uh-oh!" in post_login_rsp.text and "Your credentials are invalid" in post_login_rsp.text):
        print("Invalid credentials")
        return False

    #GOOD LOGIN, checks url to be dashboard and that a logout button is present meaning logged in
    elif post_login_rsp.url == "https://www.cecs.ucf.edu/epc/" and "logout" in post_login_rsp.text:
        print("Logged in")
        return True
    elif "Page Expired" in post_login_rsp.text:
        print("Page Expired")
        raise Exception("Page Expired")
    else:
        print("Unknown response")
        raise Exception("Unknown response")
