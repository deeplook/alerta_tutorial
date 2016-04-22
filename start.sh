#!/usr/bin/bash

source ~/.bash_profile
cd $ALERTA_TEST_DIR

echo "Starting services..."

echo "Starting MongoDB..."
./mongodb-osx-x86_64-3.2.5/bin/mongod --dbpath ./data/db > mongo.log 2>&1 &

echo "Starting Alerta development server..."
./miniconda2/bin/alertad --port 8090 > alertad.log 2>&1 &

echo "Starting Alerta dashboard..."
cd angular-alerta-webui/app
../../miniconda2/bin/python -m SimpleHTTPServer 8095 > ../../alertaui.log 2>&1 &
cd ../..

echo "Starting Jupyter, open tutorial notebook..."
./miniconda2/bin/jupyter-notebook ../tutorial.ipynb > jupyter.log 2>&1 &
