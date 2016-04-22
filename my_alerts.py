#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run periodic monitoring functions and create alerts for alerta.io.

Todo: 

- define API endpoint and key in some more global fashion.
- extract the part of deleting existing alerts into something else (decorator?)
"""


import os
import re
import sys
import json
import time
import urllib2
import warnings
import argparse
from threading import Timer
from os.path import dirname, join

import urllib3
import requests
from alerta.api import ApiClient
from alerta.alert import Alert


urllib3.disable_warnings()


alerta_endpoint = 'http://localhost:8090'
# key = 'tiPMW41QA+cVy05E7fQA/roxAAwHqZq/jznh8MOk'
api = ApiClient(endpoint=alerta_endpoint) # , key=key)
DRY_RUN = False


# helper function because many other things need an internet connection

class RepeatedTimer(object):
    # http://stackoverflow.com/questions/3393612/run-certain-code-every-n-seconds
    def __init__(self, interval, function, args=[], kwargs={}):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.daemon     = True
        self.first_run()
        self.start()

    def first_run(self):
        self.is_running = True
        # print "****", self.args, self.kwargs
        self.function(*self.args, **self.kwargs)
        self.is_running = False

    def _run(self):
        self.is_running = False
        self.start()
        # print "++++", self.args, self.kwargs
        self.function(*self.args, **self.kwargs)

    def start(self):
        if self.interval > 0 and not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

##########################

def alert_volume_not_existing(path):
    """
    Create alert if a volume does not exist, delete previous alert if it does.
    
    Command-line alternative (replace path argument):

        alerta send -r localhost -e VolumeUnavailable -E Localhost \
            -S Filesystem -s minor -t "Volume not available." -v <path>
    """

    event = 'VolumeUnavailable'
    resource = 'localhost'
    environment = 'Production'
    severity = 'minor'
    service = ['Filesystem']
    text = 'Volume not available.'
    value = path

    alert_desc = dict(resource=resource, event=event,
        environment=environment, service=service,
        severity=severity, text=text, value=value)

    if not os.path.exists(path):
        # send new alert
        alert = Alert(**alert_desc)
        result = api.send(alert)
        if result['status'] == 'error':
            print result
            # raise IndexError ## TODO: make more meaningfull exception
    else:
        # delete existing alert
        query = dict(**alert_desc)
        for alert in api.get_alerts(query=query)['alerts']:
            api.delete_alert(alert['id'])

##########################

def internet_available():
    try:
        # response = urllib2.urlopen('http://74.125.228.100', timeout=1)
        response = urllib2.urlopen('http://www.google.com', timeout=10)
        return True
    except urllib2.URLError as err:
        return False


def alert_no_internet_access(url='http://www.google.com'):
    """
    Create alert if no internet access available, delete previous alert if it is.
    
    Command-line alternative (replace path argument):

        alerta send -r network -e InternetUnavailable -E Network \
            -S Network -s critical -t "Network not available." -v <url>
    """

    event = 'InternetUnavailable'
    resource = 'network'
    environment = 'Production'
    severity = 'critical'
    service = ['Network']
    text = 'Network not available.'
    value = url

    alert_desc = dict(resource=resource, event=event,
        environment=environment, service=service,
        severity=severity, text=text, value=value)

    if not internet_available():
        if not DRY_RUN:
            # send new alert
            alert = Alert(**alert_desc)
            result = api.send(alert)
            if result['status'] == 'error':
                print result
                # raise IndexError ## TODO: make more meaningfull exception
        else:
            print alert_desc
    else:
        if not DRY_RUN:
            # delete existing alert
            query = dict(**alert_desc)
            for alert in api.get_alerts(query=query)['alerts']:
                api.delete_alert(alert['id'])

###############################

def get_conda_list(path):
    """
    Get installed packages as a dict of {name: version, ...}.
    """

    import json
    import subprocess
    cmd = "%s list --json" % path
    jsn = subprocess.check_output(cmd.split())
    pkg_list = json.loads(jsn)
    res = [item.split('-')[:2] for item in pkg_list]
    return res


def get_conda_updates(path):
    """
    Version strings are compared correctly, so 0.9.1 < 0.17.0.
    """

    # make alert suggesting latest available version if bigger than currently installed one
    import json
    import subprocess
    from packaging.version import Version
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


def alert_conda_outdated(path):
    """
    Create alert for an outdated pip package, delete previous alert if up to date.

    pip2.7 list --outdated

        ansible (1.9.4) - Latest: 2.0.0.2 [sdist]
        arrow (0.6.0) - Latest: 0.7.0 [sdist]
        astunparse (1.2.2) - Latest: 1.3.0 [sdist]
        Authomatic (0.0.13) - Latest: 0.1.0.post1 [sdist]
        ...

    conda search --outdated
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
    conda search --outdated --json

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

    from packaging.version import Version
    for (n, installed_version, latest_version) in get_conda_updates(path):
        event = 'UpdateAvailable'
        resource = n
        environment = 'Production'
        severity = 'minor'
        text = 'Installed: %s' % installed_version
        service = ['Conda']
        value = latest_version

        alert_desc = dict(resource=resource, event=event,
            environment=environment, service=service,
            severity=severity, text=text, value=value)

        if Version(installed_version) < Version(latest_version):
            if not DRY_RUN:
                # send new alert
                alert = Alert(**alert_desc)
                result = api.send(alert)
            else:
                print alert_desc

    # delete previous alerts
    for (n, installed_version) in get_conda_list(path):
        event = 'UpdateAvailable'
        resource = n
        environment = 'Production'
        severity = 'minor'
        # text = 'Installed: %s' % installed_version
        service = ['Conda']
        value = installed_version

        alert_desc = dict(resource=resource, event=event,
            environment=environment, service=service,
            severity=severity, value=value)
        if not DRY_RUN:
            query = dict(**alert_desc)
            for alert in api.get_alerts(query=query)['alerts']:
                api.delete_alert(alert['id'])
        else:
            print alert_desc

###############################

def get_kickstarter_days_left(url):
    """
    Return number of days left for a running below on kickstarter.com.

    This needs Selenium because the desired number is updated dynamically
    on the HTML page.
    
    Also, there is no public API to get it, despite the added 'stats.json'
    which gives some data, but not the number of days left, e.g.

        https://www.kickstarter.com/projects/214379695/micropython-on-the-esp8266-beautifully-easy-iot/stats.json
    """

    from selenium import webdriver
    from lxml import html

    phantomjs_path = '/Applications/Added/phantomjs-1.9.8-macosx/bin/phantomjs'
    browser = webdriver.PhantomJS(phantomjs_path)
    browser.get(url)
    content = browser.page_source
    tree = html.fromstring(content)
    xpath = '//*[@id="stats"]/div/div[3]/div/div/div/text()'
    num_days_left = tree.xpath(xpath)[0]

    return int(num_days_left)


def alert_kickstarter_days(url):
    """

    We need Selenium because the number we want is updated dynamically on the HTML page.
    And we need to scrape because there is no public API to get it, despite the following
    which gives some data, but not the number of days left:
    https://www.kickstarter.com/projects/214379695/micropython-on-the-esp8266-beautifully-easy-iot/
    """

    from os.path import dirname, basename

    num_days_left = get_kickstarter_days_left(url)
    campaign_title = basename(url) if basename(url) else dirname(url)

    event = 'CampaignEndingSoon'
    resource = campaign_title
    environment = 'Production'
    severity = 'normal'
    text = 'More than a month left.'
    if num_days_left < 7:
        severity = 'critical'
        text = 'Less than a week left.'
    elif 7 <= num_days_left < 14:
        severity = 'major'
        text = 'Less than two weeks left.'
    elif 14 <= num_days_left < 28:
        severity = 'minor'
        text = 'Less than a month left.'
    service = ['Kickstarter']
    value = str(num_days_left)

    alert_desc = dict(resource=resource, event=event,
        environment=environment, service=service,
        severity=severity, text=text, value=str(num_days_left))

    # print alert_desc

    if num_days_left < 28:
        # send new alert
        alert = Alert(**alert_desc)
        result = api.send(alert)
        if result['status'] == 'error':
            print result
            # raise IndexError ## TODO: make more meaningfull exception
    else:
        # delete existing alert
        del alert_desc['value']
        del alert_desc['severity']
        del alert_desc['text']
        query = dict(**alert_desc)
        for alert in api.get_alerts(query=query)['alerts']:
            api.delete_alert(alert['id'])

###############################

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

    from lxml import html
    res['title_contains'] = False
    if title_contains:
        tree = html.fromstring(resp.text.encode('utf-8'))
        for c in tree.head.getchildren():
            if c.tag == 'title':
                if title_contains in c.text_content():
                    res['title_contains'] = True 
                break

    return res


def alert_webpage(url, *args, **kwargs):
    info = get_webpage_info(url, *args, **kwargs)

    event = 'CheckFailed'
    resource = url
    environment = 'Production'
    severity = 'normal'
    text = 'Nothing to report.'
    service = ['WWW']
    value = 'ok'
    if info['status'] != 200:
        severity = 'major'
        text = 'Status is %d.' % info[status]
        value = info[status]
    if info['text_contains'] == False:
        severity = 'major'
        text = 'Expected text not found.'
        value = kwargs['text_contains']

    alert_desc = dict(resource=resource, event=event,
                      environment=environment, service=service,
                      severity=severity, text=text, value=value)

    if severity == 'major':
        # send new alert
        alert = Alert(**alert_desc)
        result = api.send(alert)
        # if result['status'] == 'error':
        #     print result
        #     # raise IndexError ## TODO: make more meaningfull exception
    else:
        # delete existing alert
        del alert_desc['value']
        del alert_desc['severity']
        del alert_desc['text']
        query = dict(**alert_desc)
        for alert in api.get_alerts(query=query)['alerts']:
            api.delete_alert(alert['id'])


###############################

def get_python_sites_status():
    """
    Get status of various Python-related websites.

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

    from lxml import html
    tree = html.fromstring(content)
    xpath = '//div[contains(concat(" ", normalize-space(@class), " "), " component-inner-container ")]'
    divs = tree.xpath(xpath)
    res = {}
    for div in divs:
        fields = div.text_content().strip().split()
        # filter only stuff that looks like qualified domain names
        if '.org' in fields[0]:
            res[fields[0]] = fields[-1] 

    return res


def alert_python_sites_status():
    """
    Alert if any Python-related website is not 'operational'.
    """
    statuses = get_python_sites_status()

    for domain in statuses:
        event = 'NonOperational'
        resource = domain
        environment = 'Production'
        severity = 'normal'
        text = 'Nothing to report.'
        if statuses[domain] != 'Operational':
            severity = 'major'
            text = 'Something is wrong.'
        service = ['PythonCommunity']
        value = statuses[domain]

        alert_desc = dict(resource=resource, event=event,
            environment=environment, service=service,
            severity=severity, text=text, value=value)

        if severity != 'normal':
            # send new alert
            alert = Alert(**alert_desc)
            result = api.send(alert)
            if result['status'] == 'error':
                print result
                # raise IndexError ## TODO: make more meaningfull exception
        else:
            # delete existing alert
            del alert_desc['value']
            del alert_desc['severity']
            del alert_desc['text']
            query = dict(**alert_desc)
            for alert in api.get_alerts(query=query)['alerts']:
                api.delete_alert(alert['id'])

###############################

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


def alert_no_vpn(**kwdict):
    """
    Alert if not using VPN connection.
    """

    event = 'VPNDisconnected'
    resource = 'network'
    environment = 'Production'
    severity = 'critical'
    service = ['Network']
    text = 'VPN client is disconnected.'
    value = '?'

    alert_desc = dict(resource=resource, event=event,
        environment=environment, service=service,
        severity=severity, text=text, value=value)

    if not using_vpn(**kwdict):
        if not DRY_RUN:
            # send new alert
            alert = Alert(**alert_desc)
            result = api.send(alert)
            if result['status'] == 'error':
                print result
                # raise IndexError ## TODO: make more meaningfull exception
        else:
            print alert_desc
    else:
        if not DRY_RUN:
            # delete existing alert
            query = dict(**alert_desc)
            for alert in api.get_alerts(query=query)['alerts']:
                api.delete_alert(alert['id'])

###############################

def start(*args, **kwargs):
    """
    Run monitoring functions periodically.

    Returns a list of RepeatedTimer objects, each wrapping an alert function.
    """

    alert_functions = [
        {'name': 'alert_no_vpn', 
         'repeat': 10, 
         'kwargs': {'city': 'Berlin', 'country': 'Germany'}},
        {'name': 'alert_no_internet_access', 
         'repeat': 2},
        {'name': 'alert_volume_not_existing', 
         'repeat': 2, 
         'args': ['/Volumes/Intenso64']},
        #{'name': 'alert_kickstarter_days', 
        # 'repeat': 3600, 
        # 'args': ['https://www.kickstarter.com/projects/olo3d/olo-the-first-ever-smartphone-3d-printer/description']},
        {'name': 'alert_conda_outdated', 
        'repeat': 10, 
         'args': [join(dirname(sys.executable), 'conda')]},
        {'name': 'alert_python_sites_status', 
        'repeat': 600},
        {'name': 'alert_webpage', 
         'repeat': 15, 
         'args': ['http://pythonberlin.eu.ngrok.io'], 
         'kwargs': {'text_contains': '#pythonberlin on Slack'}},
    ]

    if 'list' in kwargs:
        for item in alert_functions:
            print '  %s' % item['name']
        return []
    
    if 'name' in kwargs:
        name = kwargs['name']
        res = []
        for item in alert_functions:
            if name == item['name']:
                repeat = item['repeat']
                func = eval(name)
                args = item.get('args', [])
                kwargs = item.get('kwargs', {})
                rt = RepeatedTimer(repeat, func, args=args, kwargs=kwargs)
                res.append(rt)
                # rt.stop()
        return res
    elif 'all' in kwargs:
        res = []
        for item in alert_functions:
            repeat = item['repeat']
            func = eval(item['name'])
            args = item.get('args', [])
            kwargs = item.get('kwargs', {})
            rt = RepeatedTimer(repeat, func, args=args, kwargs=kwargs)
            res.append(rt)
            # rt.stop()
        return res


def main():
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, append=True)
        warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning, append=True)

    desc = 'Run periodic monitoring functions and create alerts for alerta.io.'
    p = argparse.ArgumentParser(description=desc)

    p.add_argument('--verbose', action='store_true',
        help='Output additional messages as we go.')
    p.add_argument('--dry', action='store_true',
        help='Dry run, writing to stdout instead of sending alerts to alerta.')
    p.add_argument('--list', action='store_true',
        help='List aert names.')
    p.add_argument('--name', metavar='ALERT_FUNC',
        help='Run monitoring functions with given name.')
    p.add_argument('--all', action='store_true',
        help='Run all monitoring functions.')

    args = p.parse_args()

    if args.dry:
        global DRY_RUN
        DRY_RUN = True

    start(args._get_args(), args._get_kwargs())


if __name__ == '__main__':
    main()
