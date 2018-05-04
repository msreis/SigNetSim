#!/bin/bash
EXEC_DIR=$PWD
CMD=$0

apt-get -qq update
apt-get install -y realpath

if [ "${CMD:0:1}" == "/" ]
then
    # absolute path
    DIR=`dirname ${CMD}`

else
    # relative path
    DIR=`dirname $( realpath $PWD/${CMD} )`

fi

INSTALL_DIR=`dirname $DIR`

# System Dependencies
apt-get install -y $( cat ${DIR}/apt_requirements )

virtualenv ${DIR}/venv

# Python Dependencies
${DIR}/venv/bin/pip install pip --upgrade

${DIR}/venv/bin/easy_install -U distribute

${DIR}/venv/bin/pip install -I setuptools --upgrade

${DIR}/venv/bin/pip install -r ${DIR}/pip_requirements

# JS Dependencies
curl -sL https://deb.nodesource.com/setup_6.x | bash -
apt-get install -y nodejs
npm install -g yarn

cd $INSTALL_DIR

yarn install

cd $EXEC_DIR
