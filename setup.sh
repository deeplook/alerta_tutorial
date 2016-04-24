#!/usr/bin/bash

# create and memorize throw-away directory
export ALERTA_TEST_DIR=$PWD/alerta_test_directory
echo "Setting up test installation folder '$ALERTA_TEST_DIR'..."
echo "export ALERTA_TEST_DIR=$ALERTA_TEST_DIR" >> ~/.bash_profile
mkdir -p $ALERTA_TEST_DIR

# install Miniconda2
# alternative(s):
# https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh
cd $ALERTA_TEST_DIR
if [ ! -f Miniconda-latest-MacOSX-x86_64.sh ]
then
    wget https://repo.continuum.io/miniconda/Miniconda-latest-MacOSX-x86_64.sh
fi
if [ ! -d miniconda2 ]
then
    bash Miniconda-latest-MacOSX-x86_64.sh -b -f -p ./miniconda2
fi

# update & install stuff
cd $ALERTA_TEST_DIR
./miniconda2/bin/pip install -U pip
./miniconda2/bin/conda install -y jupyter
./miniconda2/bin/conda install -y ipython 

if [ ! -d RISE ]
then
    git clone https://github.com/damianavila/RISE.git
    cd RISE
    ../miniconda2/bin/python setup.py install
    cd ..
fi
