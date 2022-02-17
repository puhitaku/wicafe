wicafe
======

*Automatic login utility of free Wi-Fi captive portals*


Supported public Wi-Fi services
-------------------------------

 - Wi2
   - Excelsior Caffe
   - Saint Marc Cafe
   - San'yo Shinkansen (West Japan Railway)
   - Tokai Shinkansen (Central Japan Railway)


Prerequisites
-------------

 - Python 3.7+


Install
-------

From PyPI:

```shellsession
$ pip install wicafe
```

From GitHub (directly):

```shellsession
$ pip install git+https://github.com/puhitaku/wicafe
```

From GitHub (for development):

```shellsession
$ git clone
$ pip install -e .[dev]
```


Run
---

```shellsession
$ wicafe
$ python -m wicafe  # alternative way
```

wicafe begins to poll a remote host and automatically accepts the ToS of
the captive portal when a redirection is detected.


Disclaimer
----------

 - Read and grant the Terms of Service of Wi-Fi services before using it!
 - As stated in the license, I'm not liable for any claim and violation of the ToS :wink:

