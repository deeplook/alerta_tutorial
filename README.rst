README
======

This is a repository created to get you excited about `alerta.io <http://alerta.io>`_,
a sophisticated 'meta-monitoring' solution. It tries to give you a very fast introduction to setting up a working local installation and play with your own alerts in a time-frame of 5-10 minutes.


Getting started
---------------

This is the suggested sequence of steps to get started:

- clone this repo into a local directory using ``git clone https://github.com/deeplook/alerta_tutorial.git``
- change into this directory, ``cd alerta_tutorial``
- perform baseline setup, ``bash setup.sh`` (install Miniconda2, IPython and Jupyter + reveal.js plugin)
- perform installation, ``bash setup.sh`` (MongoDB, Alerta server and dashboard)
- start services, ``bash start.sh`` (MongoDB, Alerta server and dashboard, open Jupyter notebook ``tutorial.jpynb``
- in the notebook click on the button with a text pop-up label "Enter/Exit Live Reveal Slideshow"
- execute cells and play with your own alerts!

To clean up by stopping all services and removing the installation directory, simply do ``bash cleanup.sh``.
