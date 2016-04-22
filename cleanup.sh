#!/usr/bin/env/bash

source ~/.bash_profile

echo "Cleaning up processes and installation folder '$ALERTA_TEST_DIR' ..."
pkill -I -f "mongod --dbpath ./data/db"
pkill -I -f "./miniconda2/bin/alertad --port 8090"
pkill -I -f "../../miniconda2/bin/python -m SimpleHTTPServer 8095"
pkill -I -f "my_alerts.py"
pkill -I -f "jupyter-notebook"
read -p "Click ENTER to remove installation folder, or Ctrl-C to stop here."
sudo rm -rf $ALERTA_TEST_DIR
sed -i .bak '/ALERTA_TEST_DIR/d' ~/.bash_profile
# export ALERTA_TEST_DIR=
