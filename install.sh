#!/usr/bin/bash

source ~/.bash_profile

echo "Installing..."

cd $ALERTA_TEST_DIR

# please adapt if your OS != MacOS X...
wget https://fastdl.mongodb.org/osx/mongodb-osx-x86_64-3.2.4.tgz
tar xfz mongodb-osx-x86_64-3.2.4.tgz
mkdir -p ./data/db
chmod g+w ./data ./data/db

./miniconda2/bin/pip install "alerta-server>=4.7.12"

git clone https://github.com/alerta/angular-alerta-webui.git
sed -i .bak 's/8080/8090/g' $ALERTA_TEST_DIR/angular-alerta-webui/app/config.js
