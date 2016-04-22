Alerta Tutorial
===============

This is a repository created to get you excited about `alerta.io <http://alerta.io>`_,
a sophisticated event monitoring solution. This tutorial wants to provide you with a zero effort, risk-free opportunity to install from scratch all you need to play with your own alerts, including Python, MongoDB, Alerta server and dashboard as well as a set of sample alerts. Plus an interactive Jupyter notebook serving as a tutorial and presentation. All this in abou 10 minutes! (If you are not on MacOS X, you will have to make very small changes manually, first.)


Getting started
---------------

This is the suggested sequence of steps to get started:

- clone this repo into a local directory using ``git clone https://github.com/deeplook/alerta_tutorial.git``
- change into this directory, ``cd alerta_tutorial``
- perform baseline setup, ``bash setup.sh`` (install Miniconda2, IPython and Jupyter + reveal.js plugin)
- perform installation, ``bash install.sh`` (MongoDB, Alerta server and dashboard)
- start services, ``bash start.sh`` (MongoDB, Alerta server and dashboard, open Jupyter notebook ``tutorial.jpynb``
- in the notebook click on the button with a text pop-up label "Enter/Exit Live Reveal Slideshow"
- execute cells and play with your own alerts!

To clean up by stopping all services and removing the installation directory, simply do ``bash cleanup.sh``.
