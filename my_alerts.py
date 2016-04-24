#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run monitoring functions periodically and create alerts for alerta.io.
"""

import os
import sys
import warnings
import argparse
import threading
from os.path import dirname, basename, join

import urllib3
import requests
from packaging.version import Version
from alerta.api import ApiClient
from alerta.alert import Alert

import utils


urllib3.disable_warnings()


alerta_endpoint = 'http://localhost:8090'
api = ApiClient(endpoint=alerta_endpoint)
DRY_RUN = False


#
# alert monitoring functions, kind of wrapping functions in utils
#

def alert_volume_not_existing(path):
    """
    Alert if a volume does not exist, delete previous alert if it does.
    
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

    if not utils.volume_is_mounted(path):
        # send new alert
        alert = Alert(**alert_desc)
        result = api.send(alert)
        if result['status'] == 'error':
            print result
            # raise IndexError ## TODO: make more meaningful exception
    else:
        # delete existing alert
        query = dict(**alert_desc)
        for alert in api.get_alerts(query=query)['alerts']:
            api.delete_alert(alert['id'])



def alert_no_internet_access(url='http://www.google.com'):
    """
    Alert if no internet access available, delete previous alert if it is.
    
    Command-line alternative (replace path argument)::

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

    if not utils.internet_available(url):
        if not DRY_RUN:
            # send new alert
            alert = Alert(**alert_desc)
            result = api.send(alert)
            if result['status'] == 'error':
                print result
                # raise IndexError ## TODO: make more meaningful exception
        else:
            print alert_desc
    else:
        if not DRY_RUN:
            # delete existing alert
            query = dict(**alert_desc)
            for alert in api.get_alerts(query=query)['alerts']:
                api.delete_alert(alert['id'])


def alert_conda_outdated(path):
    """
    Alert for an outdated conda package, delete previous alert if up to date.
    """

    for (n, installed_version, latest_version) in utils.get_conda_updates(path):
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
    for (n, installed_version) in utils.get_conda_list(path):
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


def alert_kickstarter_days(url):
    """
    Alert if a kickstarter campaign will end, soon.

    We need Selenium because the number we want is updated dynamically on the
    HTML page. And we need to scrape because there is no public API to get it,
    despite the following which gives some data, but not the number of days
    left:

    https://www.kickstarter.com/projects/214379695/micropython-on-the-esp8266-beautifully-easy-iot/
    """
    # phantomjs <= 1.9.8 will not work...
    phantomjs_path = 'phantomjs-2.1.1-macosx/bin/phantomjs'
    browser = utils.webdriver.PhantomJS(phantomjs_path)
    num_days_left = utils.get_kickstarter_days_left(url, browser)
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

    if num_days_left < 28:
        # send new alert
        alert = Alert(**alert_desc)
        result = api.send(alert)
        if result['status'] == 'error':
            print result
            # raise IndexError ## TODO: make more meaningful exception
    else:
        # delete existing alert
        del alert_desc['value']
        del alert_desc['severity']
        del alert_desc['text']
        query = dict(**alert_desc)
        for alert in api.get_alerts(query=query)['alerts']:
            api.delete_alert(alert['id'])


def alert_webpage(url, *args, **kwargs):
    """
    Alert if a webpage has unexpected content.
    """
    info = utils.get_webpage_info(url, *args, **kwargs)

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
        #     # raise IndexError ## TODO: make more meaningful exception
    else:
        # delete existing alert
        del alert_desc['value']
        del alert_desc['severity']
        del alert_desc['text']
        query = dict(**alert_desc)
        for alert in api.get_alerts(query=query)['alerts']:
            api.delete_alert(alert['id'])


def alert_python_sites_status():
    """
    Alert if any Python-related website infrastructure is not 'operational'.
    """
    statuses = utils.get_python_sites_status()

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
                # raise IndexError ## TODO: make more meaningful exception
        else:
            # delete existing alert
            del alert_desc['value']
            del alert_desc['severity']
            del alert_desc['text']
            query = dict(**alert_desc)
            for alert in api.get_alerts(query=query)['alerts']:
                api.delete_alert(alert['id'])


def alert_no_vpn(**kwdict):
    """
    Alert if we don't use a VPN connection.
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

    if not utils.using_vpn(**kwdict):
        if not DRY_RUN:
            # send new alert
            alert = Alert(**alert_desc)
            result = api.send(alert)
            if result['status'] == 'error':
                print result
                # raise IndexError ## TODO: make more meaningful exception
        else:
            print alert_desc
    else:
        if not DRY_RUN:
            # delete existing alert
            query = dict(**alert_desc)
            for alert in api.get_alerts(query=query)['alerts']:
                api.delete_alert(alert['id'])


#
# run functions periodically using threads
#

class RepeatedTimer(object):
    """
    A class wrapping a function to be called periodically inside a thread.

    The wrapped function is called the first time immediately after creating
    an instance of this class.

    Examples::

        rt = RepeatedTimer(repeat, func, args=args, kwargs=kwargs)
        rt.stop()
    """
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
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


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
        
        {'name': 'alert_kickstarter_days',
         'repeat': 60 * 60 * 6,
         'args': ['https://www.kickstarter.com/projects/olo3d/olo-the-first-ever-smartphone-3d-printer/description']},
        
        {'name': 'alert_conda_outdated',
        'repeat': 10,
         'args': [join(dirname(sys.executable), 'conda')]},
        
        {'name': 'alert_python_sites_status',
        'repeat': 60 * 10},
        
        {'name': 'alert_webpage',
         'repeat': 60,
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
        return res


#
# main
#

def main():
    """
    Command-line interface.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, append=True)
        warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning, append=True)

    desc = 'Run custom periodic monitoring functions for alerta.io.'
    p = argparse.ArgumentParser(description=desc)

    p.add_argument('--verbose', action='store_true',
        help='Output additional messages as we go.')
    p.add_argument('--dry', action='store_true',
        help='Dry run, writing to stdout instead of sending alerts to alerta (experimental).')
    p.add_argument('--list', action='store_true',
        help='List available monitoring function names.')
    p.add_argument('--name', metavar='FUNC_NAME',
        help='Run one monitoring function with given name.')
    p.add_argument('--all', action='store_true',
        help='Run all monitoring functions.')

    args = p.parse_args()

    if args.dry:
        global DRY_RUN
        DRY_RUN = True

    start(args._get_args(), args._get_kwargs())


if __name__ == '__main__':
    main()
