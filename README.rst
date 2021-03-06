Alerta Tutorial
===============

This tutorial was created to get you excited about `alerta.io <http://alerta.io>`_,
a sophisticated, general-purpose event monitoring solution. 

The idea is to provide you with a zero effort, risk-free opportunity to install from scratch all you need to play with your own alerts, including Python, MongoDB, Alerta server and dashboard as well as a set of sample alerts. Plus an interactive Jupyter notebook serving as a tutorial and presentation! And all this in about 15 minutes with a modern internet connection! (If you are not on MacOS X, you will have to make very small changes manually, first.)


Getting started
---------------

This is the suggested sequence of steps to get started.

TLDR;
.....

.. code-block:: console

    git clone https://github.com/deeplook/alerta_tutorial.git
    cd alerta_tutorial
    bash setup.sh
    bash install.sh
    bash custom.sh
    bash start.sh


Details
.......

- clone this repo into a local directory and change into to:

  .. code-block:: console

     git clone https://github.com/deeplook/alerta_tutorial.git
     cd alerta_tutorial

- perform baseline setup (install Miniconda2, IPython and Jupyter + reveal.js plugin):

  .. code-block:: console

     bash setup.sh

- perform installation (MongoDB, Alerta server and dashboard):

  .. code-block:: console

     bash install.sh

- install dependencies for custom alerts (some Python packages, plus PhantomJS):

  .. code-block:: console

     bash custom.sh

- start services (MongoDB, Alerta server and dashboard, also opens Jupyter notebook ``tutorial.jpynb``:

  .. code-block:: console

     bash start.sh

In the notebook click on the button with a text pop-up label "Enter/Exit Live Reveal Slideshow", then execute the cells and play with your own alerts!


Clean Up
........

To clean up by stopping all services and removing everything built in the installation directory, simply do:

.. code-block:: console

   bash cleanup.sh
