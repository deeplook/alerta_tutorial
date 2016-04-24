#!/usr/bin/bash

source ~/.bash_profile

echo "Installing..."

cd $ALERTA_TEST_DIR

# please adapt if your OS != MacOS X...
# alternative(s):
# https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-debian71-3.2.5.tgz
cd $ALERTA_TEST_DIR
if [ ! -f mongodb-osx-x86_64-3.2.5.tgz ]
then
	wget https://fastdl.mongodb.org/osx/mongodb-osx-x86_64-3.2.5.tgz
fi
if [ ! -d mongodb-osx-x86_64-3.2.5 ]
then
    tar xfz mongodb-osx-x86_64-3.2.5.tgz
    mkdir -p ./data/db
    chmod g+w ./data ./data/db
fi

./miniconda2/bin/pip install "alerta-server"

if [ ! -d angular-alerta-webui ]
then
    git clone https://github.com/alerta/angular-alerta-webui.git
fi

sed -i .bak 's/8080/8090/g' $ALERTA_TEST_DIR/angular-alerta-webui/app/config.js
