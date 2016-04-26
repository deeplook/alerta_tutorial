
# coding: utf-8

# # Alerta Tutorial
# 
# A tutorial from scratch to writing your own alerts using alerta.io.

# In[ ]:

from IPython.display import HTML
HTML('<iframe src="http://alerta.io" width="100%" height="500"></iframe>')


# ## Prerequisites
# 
# Assumed environment (tested on Mac OS X):
# 
# - POSIX OS
# - bash
# - git
# - pkill
# - wget

# ## Setup
# 
# Components installed during the baseline setup (before you can actually see this notebook), executed with `bash setup.sh`:
# 
# - Miniconda2
# - pip
# - jupyter
# - ipython
# - RISE plugin for jupyter

# ## Install the real thing(s)
# 
# Components needed for Alerta, executed with `bash install.sh`:
# 
# - MongoDB
# - Alerta server
# - Alerta Dashboard

# ## Install custom packages and tools
# 
# The following dependencies for creating custom alerts from in the included examples can be installed with `bash custom.sh`:
# 
# - lxml
# - url3
# - packaging
# - selenium
# - PhantomJS

# ## Start everything
# 
# Processes to start (Jupyter doesn't support background processes) with `bash start.sh`:
# 
# - MongoDB
# - Alerta server/API
# - Alerta Dashboard
# - Jupyter tutorial/presentation (this notebook file)

# ## Alerta API

# In[ ]:

from IPython.display import HTML
HTML('<iframe src="http://localhost:8090" width="100%" height="500"></iframe>')


# ## Alerta Dashboard

# In[ ]:

from IPython.display import HTML
HTML('<iframe src="http://localhost:8095" width="100%" height="500"></iframe>')


# ## Alerta Top
# 
# Run this command in a Jupyter terminal (or any other):
# 
# ```bash
# ./miniconda2/bin/alerta --endpoint http://localhost:8090 top
# ```

# ## Rolling Your Own Alerts

# ### Simple, Unix style

# In[ ]:

get_ipython().system(u' cd $ALERTA_TEST_DIR && ./miniconda2/bin/alerta     --endpoint-url "http://localhost:8090"     send -E Production -r localhost -e VolUnavailable          -S Filesystem -v ERROR -s minor          -t "/Volumes/XYZ not available."')


# In[ ]:

get_ipython().system(u' cd $ALERTA_TEST_DIR && ./miniconda2/bin/alerta     --endpoint-url "http://localhost:8090"     delete')


# ### Same Thing, Python style

# In[ ]:

from alerta.api import ApiClient
from alerta.alert import Alert

api = ApiClient(endpoint='http://localhost:8090')
alert = Alert(resource='localhost', event='VolUnavailable',
              service=['Filesystem'], environment='Production',
              value='ERROR', severity='minor')
res = api.send(alert)


# ## Custom Alerts

# ### Remember, you can do amazing stuff…

# In[ ]:

import utils
utils.volume_is_mounted('/Volumes/Intenso64')


# In[ ]:

utils.internet_available()


# In[ ]:

utils.using_vpn(city='Berlin', country='Germany')


# In[ ]:

utils.get_python_sites_status()


# In[ ]:

from IPython.display import HTML
HTML('<iframe src="https://status.python.org" width="100%" height="500"></iframe>')


# In[ ]:

utils.get_webpage_info('http://www.python.org', title_contains='Python')


# In[ ]:

import sys
from os.path import join, dirname


# In[ ]:

conda_path = join(dirname(sys.executable), 'conda')
conda_path


# In[ ]:

utils.get_conda_list(conda_path)


# In[ ]:

utils.get_conda_updates(conda_path)


# In[ ]:

ks_url = 'https://www.kickstarter.com/projects/udoo/udoo-x86-the-most-powerful-maker-board-ever/'
utils.get_kickstarter_days_left(ks_url)
# uses Firefox as it doesn't need a special driver installation


# In[ ]:

phantomjs_path = './alerta_test_directory/phantomjs-2.1.1-macosx/bin/phantomjs'
browser = utils.webdriver.PhantomJS(phantomjs_path)
utils.get_kickstarter_days_left(ks_url, browser)


# ### Get Alerts to Get Things Done
# 
# Watch this dashboard as you perform changes on the next slides!

# In[ ]:

from IPython.display import HTML
HTML('<iframe src="http://localhost:8095" width="100%" height="500"></iframe>')


# In[ ]:

import my_alerts as ma
ma.start(list=True)


# In[ ]:

rts = ma.start(name='alert_conda_outdated')
rts


# In[ ]:

import subprocess
cmd = "%s install -y sqlite==3.8.4.1" % conda_path
print subprocess.check_output(cmd.split())


# In[ ]:

cmd = "%s update -y sqlite" % conda_path
print subprocess.check_output(cmd.split())


# In[ ]:

rts[0].stop()


# ### Start Playing
# 
# Do any of these things and watch the effects in the Alerta dashboard:
# 
# - closing and reopening your internet connection
# - disconnecting and reconnecting your VPN client
# - mounting and ejecting a volume (named `Intenso64` above)
# - then, look at `my_alerts.py` and create your own!

# ## Conclusions
# 
# - not mentioned: third-party [integrations/plugins](https://github.com/alerta/alerta-contrib) for Alerta
# - other alerting ideas:
#   - thresholds on bank accounts
#   - rules in sensor networks
# - Happy Alerting!
