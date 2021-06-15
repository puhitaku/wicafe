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


def main():
    while True:
        loop()


def loop():
    """The main loop."""

    res = watch_connection()
    location = res.headers.get('Location')

    # Detect captive portals
    # Wi2
    m = wi2.match(location)
    if m is not None and res.status_code == redirect:
        print('Logging in to Wi2 captive portal')
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

    # TODO: add other services!


def watch_connection() -> req.Response:
    """Watch internet connection and return a response if it detected a failure."""

    reachable = False

    while True:
        try:
            res = req.get(endpoint, allow_redirects=False, timeout=5)
        except req.Timeout:
            print(f'Timed out: GET {endpoint}')
            reachable = False
            time.sleep(10)
            continue

        if res.status_code == ok:
            if not reachable:
                print('The internet is live')
            reachable = True
            pass
        else:
            retry = req.get(endpoint, allow_redirects=False, timeout=5)
            if retry.status_code != ok:
                print('Detected disconnection')
                return res

        time.sleep(10)


if __name__ == '__main__':
    main()
