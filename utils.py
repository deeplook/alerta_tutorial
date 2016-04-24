#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Collection of a few more or less useful utility functions.
"""

import json
import urllib2
import subprocess
from os.path import dirname, join, exists

import requests
from packaging.version import Version
from selenium import webdriver
from lxml import html as lxml_html


def volume_is_mounted(path):
    """
    Is the volume with the given path mounted?
    """
    return exists(path)


def internet_available(url='http://www.google.com'):
    """
    Test if we have a working internet connection.
    """
    try:
        # response = urllib2.urlopen('http://74.125.228.100', timeout=1)
        response = urllib2.urlopen(url, timeout=10)
        return True
    except urllib2.URLError as err:
        return False


def using_vpn(**kwdict):
    """
    Do IP check to determine if we use a VPN connection.

    Returns True/False or None, if check failed. False (no VPN) is returned
    here when all positional parameters are found with their respective values
    in the response from ``http://ip-api.com/json`` (limited to 150 requests/min).

    Example ip-api.com response without VPN:

        {u'as': u'AS3320 Deutsche Telekom AG',
         u'city': u'Berlin',
         u'country': u'Germany',
         u'countryCode': u'DE',
         u'isp': u'Deutsche Telekom AG',
         u'lat': 52.5167,
         u'lon': 13.4,
         u'org': u'Deutsche Telekom AG',
         u'query': u'93.220.83.107',
         u'region': u'BE',
         u'regionName': u'Land Berlin',
         u'status': u'success',
         u'timezone': u'Europe/Berlin',
         u'zip': u'10317'}

    Example ip-api.com response with VPN:

        {u'as': u'AS16509 Amazon.com, Inc.',
         u'city': u'Dublin',
         u'country': u'Ireland',
         u'countryCode': u'IE',
         u'isp': u'Amazon Technologies',
         u'lat': 53.3331,
         u'lon': -6.2489,
         u'org': u'Amazon.com',
         u'query': u'52.31.80.249',
         u'region': u'L',
         u'regionName': u'Leinster',
         u'status': u'success',
         u'timezone': u'Europe/Dublin',
         u'zip': u''}

    Examples:

        # with VPN
        >>> using_vpn(city='Berlin', country='Germany')
        True

        # without VPN
        >>> using_vpn(city='Berlin', country='Germany')
        False
    """

    info = requests.get('http://ip-api.com/json').json()
    status = info['status'].lower()
    if status == 'fail':
        return None
    elif status == 'success':
        result_dict = {k: info[k] for k in kwdict}
        if result_dict == kwdict:
            return False
        else: 
            return True
    return None


def get_conda_list(path):
    """
    Get a list of installed conda packages.

    Returns a list of (pkg_name, inst_version) tuples.
    """
    cmd = "%s list --json" % path
    jsn = subprocess.check_output(cmd.split())
    pkg_list = json.loads(jsn)
    res = [item.split('-')[:2] for item in pkg_list]
    return res


def get_conda_updates(path):
    """
    Get a list of outdated installed conda packages.

    Returs a list of (pkg_name, inst_version, available_version) tuples.
    Version strings are compared correctly, e.g. 0.9.1 < 0.17.0.

    conda search --outdated::
        {
            pygments                     1.5                      py33_0  defaults        
                                         1.5                      py27_0  defaults        
                                         1.5                      py26_0  defaults        
                                         1.6                      py34_0  defaults        
                                         1.6                      py33_0  defaults        
                                         1.6                      py27_0  defaults        
                                         1.6                      py26_0  defaults        
                                         2.0.1                    py34_0  defaults        
                                         2.0.1                    py33_0  defaults        
                                         2.0.1                    py27_0  defaults        
                                         2.0.1                    py26_0  defaults        
                                         2.0.2                    py35_0  defaults        
                                         2.0.2                    py34_0  defaults        
                                         2.0.2                    py33_0  defaults        
                                      *  2.0.2                    py27_0  defaults        
                                         2.0.2                    py26_0  defaults        
                                         2.1                      py35_0  defaults        
                                         2.1                      py34_0  defaults        
                                         2.1                      py27_0  defaults
            ...
        }

    conda search --outdated --json::

      "pygments": [
        {
          "build": "py33_0", 
          "build_number": 0, 
          "channel": "defaults", 
          "date": "2014-08-22", 
          "depends": [
            "python 3.3*"
          ], 
          "extracted": false, 
          "features": [], 
          "fn": "pygments-1.5-py33_0.tar.bz2", 
          "full_channel": "https://repo.continuum.io/pkgs/free/osx-64/", 
          "installed": false, 
          "license": "BSD", 
          "md5": "a3d287301e118c16508f2d721d94c26e", 
          "name": "pygments", 
          "org_name": "Pygments", 
          "requires": [], 
          "size": 726114, 
          "type": null, 
          "version": "1.5"
        }, 
        ...
    ]
    """
    cmd = "%s search --outdated --json" % path
    jsn = subprocess.check_output(cmd.split())
    j = json.loads(jsn)
    jj = dict([(k, v) for (k, v) in j.items() if v])
    outdated_names = jj.keys()
    result = []
    for n in outdated_names:
        pkgs = jj[n]
        installed_version = [p for p in pkgs if p['installed'] == True][0]['version']
        try:
            # barfs at Version('2012d')
            pkgs.sort(key=lambda p: Version(p['version']))
        except:
            continue
        latest_version = pkgs[-1]['version']
        result.append((n, installed_version, latest_version))
    return result


def get_pip_updates(path):
    """
    Get a list of outdated installed pip packages.

    This is harder to implement, because pip doesn't provide nice JSON output...

    pip2.7 list --outdated::
        ansible (1.9.4) - Latest: 2.0.0.2 [sdist]
        arrow (0.6.0) - Latest: 0.7.0 [sdist]
        astunparse (1.2.2) - Latest: 1.3.0 [sdist]
        Authomatic (0.0.13) - Latest: 0.1.0.post1 [sdist]
        ...
    """
    raise NotImplementedError


def get_webpage_info(url, title_contains=None, text_contains=None):
    """
    Return some info for a given web page.

    url: the URL of the webpage.
    title_contains: a string to be searched in the HTML title element
    text_contains: a string to be searched in the full HTML source

    Result is a dict like this::

        {'headers': ..., 
         'status': 200,
         'text_contains': False,
         'title_contains': False}
    """
    ## TODO: catch access error:
    resp = requests.get(url)

    res = {
        'headers': resp.headers,
        'status': resp.status_code
    }

    res['text_contains'] = False
    if text_contains and text_contains in resp.text:
        res['text_contains'] = True

    res['title_contains'] = False
    if title_contains:
        tree = lxml_html.fromstring(resp.text.encode('utf-8'))
        for c in tree.head.getchildren():
            if c.tag == 'title':
                if title_contains in c.text_content():
                    res['title_contains'] = True 
                break

    return res


def get_python_sites_status():
    """
    Get status of various websites listed on from https://status.python.org.

    Result is something like this (where other status values are unknown, yet)::

        {'docs.python.org': 'Operational',
         'hg.python.org': 'Operational',
         'mail.python.org': 'Operational',
         'pypi.python.org': 'Operational',
         'pypy.org': 'Operational',
         'python.org': 'Operational',
         'speed.pypy.org': 'Operational',
         'wiki.python.org': 'Operational'}

    All information comes from from https://status.python.org only.
    It's not quite clear which other values are used apart from 'Operational'.
    """

    url = 'https://status.python.org'
    resp = requests.get(url)
    content = resp.content

    tree = lxml_html.fromstring(content)
    xpath = '//div[contains(concat(" ", normalize-space(@class), " "), " component-inner-container ")]'
    divs = tree.xpath(xpath)
    res = {}
    for div in divs:
        fields = div.text_content().strip().split()
        # filter only stuff that looks like qualified domain names
        if '.org' in fields[0]:
            res[fields[0]] = fields[-1] 

    return res


def get_kickstarter_days_left(url, browser=None):
    """
    Return number of days left until the end of a Kickstarter campaign.

    This needs Selenium because the desired number is updated dynamically
    on the HTML page.
    
    Also, there is no public API to get it, despite the added '/stats.json'
    which gives some data, but not the number of remaining days, e.g.

        https://www.kickstarter.com/projects/214379695/micropython-on-the-esp8266-beautifully-easy-iot/stats.json
        https://www.kickstarter.com/projects/udoo/udoo-x86-the-most-powerful-maker-board-ever

    Unsurprisingly, finished campaigns don't contain this number, anymore.
    """
    # phantomjs <= 1.9.8 will not work...
    # phantomjs_path = '/Applications/Added/phantomjs-2.1.1-macosx/bin/phantomjs'
    # browser = webdriver.PhantomJS(phantomjs_path)
    browser = browser or webdriver.Firefox()
    browser.get(url)
    content = browser.page_source
    tree = lxml_html.fromstring(content)
    xpath = '//*[@id="stats"]/div/div[3]/div/div/div/text()'
    try:
        num_days_left = tree.xpath(xpath)[0]
        browser.quit()
        return int(num_days_left)
    except:
        return None
