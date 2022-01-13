#!/usr/bin/env python3

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
wi2 = re.compile('https://service\.wi2\.ne\.jp/.+')

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
    except:
        if first or internet_available:
            print('The internet is not available at present')
            print('Hint: A default route may not be reachable if the OS detected a captive portal.')
            print('      Please close the login window opened by the OS, if any.')
        return

    if res is not None and res.status_code == ok:
        if not internet_available:
            print('The internet is available')
            internet_available = True
    else:
        retry = knock()
        if retry is not None and retry.status_code != ok:
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

        try:
            res = sess.get(location)
        except:
            print('Wi2: Failed to GET the forwarded location')
            return

        if res.status_code != ok:
            print('Wi2: Failed to jump to the captive portal')
            return

        try:
            res = sess.post(
                'https://service.wi2.ne.jp/wi2auth/xhr/login',
                json={'login_method': 'onetap', 'login_params': {'agree': '1'}},
            )
        except:
            print('Wi2: Failed to POST the login form')
            return

        if res.status_code != ok:
            print('Wi2: Failed to POST an XHR')
            return

        print('Wi2: Successfully logged in')

    res = knock()
    if res is not None and res.status_code == ok:
        print('The internet is available')
        internet_available = True

    # TODO: add other services!


def knock():
    try:
        return req.get(endpoint, allow_redirects=False, timeout=5)
    except:
        return None


if __name__ == '__main__':
    main()
