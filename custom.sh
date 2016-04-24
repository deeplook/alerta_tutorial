#!/usr/bin/bash

source ~/.bash_profile

echo "Installing custom stuff..."

cd $ALERTA_TEST_DIR

./miniconda2/bin/conda install -y lxml
./miniconda2/bin/pip install urllib3
./miniconda2/bin/pip install packaging
./miniconda2/bin/pip install selenium

# please adapt if your OS != MacOS X...
# alternative(s):
# https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
cd $ALERTA_TEST_DIR
if [ ! -f phantomjs-2.1.1-macosx.zip ]
then
    wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-macosx.zip
fi
if [ ! -d phantomjs-2.1.1-macosx ]
then
    unzip phantomjs-2.1.1-macosx.zip
fi
