#!/usr/bin/bash

source ~/.bash_profile

echo "Starting services..."

cd $ALERTA_TEST_DIR

./mongodb-osx-x86_64-3.2.4/bin/mongod --dbpath ./data/db > mongo.log 2>&1 &

./miniconda2/bin/alertad --port 8090 > alertad.log 2>&1 &

cd angular-alerta-webui/app
../../miniconda2/bin/python -m SimpleHTTPServer 8095 > ../../alertaui.log 2>&1 &
cd ../..

# run Jupyter notebook tutorial
./miniconda2/bin/jupyter-notebook ../tutorial.ipynb > jupyter.log 2>&1 &
