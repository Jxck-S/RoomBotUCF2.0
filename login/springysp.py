import requests
def springy_sp(session, saml_response, relay_state):
    headers = {
        'authority': 'libauth.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://federation.net.ucf.edu',
        'pragma': 'no-cache',
        'referer': 'https://federation.net.ucf.edu/',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

    data = {
        'SAMLResponse': saml_response,
        'RelayState': relay_state
    }

    response = session.post('https://libauth.com/saml/module.php/saml/sp/saml2-acs.php/springy-sp', headers=headers, data=data, allow_redirects=True)
    return response