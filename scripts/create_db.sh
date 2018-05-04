#!/bin/bash
EXEC_DIR=$PWD
CMD=$0

if [ "${CMD:0:1}" == "/" ]
then
    # absolute path
    DIR=`dirname ${CMD}`

else
    # relative path
    DIR=`dirname $( realpath $PWD/${CMD} )`

fi
INSTALL_DIR=`dirname $DIR`

cd ${INSTALL_DIR}

mkdir -p ${INSTALL_DIR}/static
mkdir -p ${INSTALL_DIR}/tmp

if [ ! -d ${INSTALL_DIR}/data/db ]
then

    mkdir -p ${INSTALL_DIR}/data/db
    mkdir -p ${INSTALL_DIR}/data/media
    mkdir -p ${INSTALL_DIR}/data/settings

fi

python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput > /dev/null

chgrp -R www-data ${INSTALL_DIR}/data
chmod -R 664 ${INSTALL_DIR}/data
find ${INSTALL_DIR}/data -type d  -exec chmod 775 {} \;

chgrp -R www-data ${INSTALL_DIR}/tmp
chmod -R 664 ${INSTALL_DIR}/tmp
find ${INSTALL_DIR}/tmp -type d  -exec chmod 775 {} \;

chgrp -R www-data ${INSTALL_DIR}/signetsim/settings/wsgi.py
chmod -R 664 ${INSTALL_DIR}/signetsim/settings/wsgi.py

cd $EXEC_DIR
