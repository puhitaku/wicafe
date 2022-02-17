#!/usr/bin/env python3

import re
import time

import requests as req
from requests.status_codes import codes

# Status codes
ok = codes.ok
redirect = codes.found

# Endpoint for connection test
endpoint = 'http://neverssl.com/'

# Rules to match Cafe Wi-Fi captive portals
# Wi2 (Wire and Wireless)
wi2_re = re.compile(r'https://service\.wi2\.ne\.jp/.+')

internet_available = True  # be able to communicate with the endpoint


def main():
    """The main loop."""

    if knock() is not None:
        print('The internet is available')

    while True:
        watch()
        time.sleep(10)


def watch():
    global internet_available

    res = knock()
    if res is None:
        if internet_available:
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
            login(retry)


def login(res: req.Response):
    """Log you in."""

    global internet_available
    location = res.headers.get('Location')
    if location is None:
        print('Wi2: the response lacks Location header, aborting')
        return

    # Detect captive portals

    # Wi2
    m = wi2_re.match(location)
    if m is not None and res.status_code == redirect:
        print('Detected Wi2 AP')
        sess = req.Session()

        try:
            res = sess.get(location)
        except:
            print('Wi2: Failed to GET the forwarded location')
            return

        if res.status_code != ok:
            print('Wi2: Failed to jump to the captive portal')
            return

        if 'shinkansen' in res.url:
            print('Wi2 (Shinkansen): Logging in')
            wi2_shinkansen(sess)
        else:
            print('Wi2: Logging in')
            wi2(sess)

    res = knock()
    if res is not None and res.status_code == ok:
        print('The internet is available')
        internet_available = True


def wi2(sess: req.Session):
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


def wi2_shinkansen(sess: req.Session):
    try:
        res = sess.post(
            'https://service.wi2.ne.jp/wi2auth/shin_xhr/login',
            json={
                "login_method": "lgovpre",
                "login_params": {"email": "a@example.com", "lang": "ja"},
            },
        )
    except:
        print('Wi2 (Shinkansen): Failed to POST the login form')
        return

    if res.status_code != ok:
        print('Wi2 (Shinkansen): Failed to POST an XHR')
        return

    print('Wi2 (Shinkansen): Successfully logged in')


def knock():
    try:
        return req.get(endpoint, allow_redirects=False, timeout=5)
    except:
        return None


if __name__ == '__main__':
    main()
