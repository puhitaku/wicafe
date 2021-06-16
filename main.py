import re
import time

import requests as req
from requests.status_codes import codes

# Status codes
ok = codes.ok
redirect = codes.found
auth_required = codes.network_authentication_required

# Endpoint for connection test
endpoint = 'http://neverssl.com/'

# Rules to match Cafe Wi-Fi captive portals

# Wi2 (Wire and Wireless)
wi2 = re.compile('https://service\.wi2\.ne\.jp/wi2auth/.+')

first = True
internet_available = False  # be able to communicate with the endpoint


def main():
    """The main loop."""

    global first

    while True:
        watch()
        first = False
        time.sleep(10)


def watch():
    global first, internet_available

    try:
        res = knock()
    except (req.ConnectionError, req.Timeout):
        if first or internet_available:
            print('The internet is not available at present')
            print('Hint: A default route may not be reachable if the OS detected a captive portal.')
            print('      Please close the login window opened by the OS, if any.')
        return

    if res.status_code == ok:
        if not internet_available:
            print('The internet is available')
            internet_available = True
    else:
        retry = knock()
        if retry.status_code != ok:
            print('Detected a redirection')
            login(res)


def login(res: req.Response):
    """Log you in."""

    global internet_available
    location = res.headers.get('Location')

    # Detect captive portals

    # Wi2
    m = wi2.match(location)
    if m is not None and res.status_code == redirect:
        print('Wi2: Logging in')
        sess = req.Session()

        res = sess.get(location)
        if res.status_code != ok:
            print('Wi2: Failed to jump to the captive portal')
            return

        res = sess.post(
            'https://service.wi2.ne.jp/wi2auth/xhr/login',
            json={'login_method': 'onetap', 'login_params': {'agree': '1'}},
        )
        if res.status_code != ok:
            print('Wi2: Failed to POST an XHR')
            return

        print('Wi2: Successfully logged in')

    res = knock()
    if res.status_code == ok:
        print('The internet is available')
        internet_available = True

    # TODO: add other services!


def knock():
    return req.get(endpoint, allow_redirects=False, timeout=5)


if __name__ == '__main__':
    main()
