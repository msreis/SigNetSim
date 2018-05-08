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


${INSTALL_DIR}/venv/bin/python manage.py makemigrations --noinput
${INSTALL_DIR}/venv/bin/python manage.py migrate --noinput
${INSTALL_DIR}/venv/bin/python manage.py collectstatic --noinput > /dev/null

chgrp -R www-data ${INSTALL_DIR}/signetsim/settings/wsgi.py
chmod -R 664 ${INSTALL_DIR}/signetsim/settings/wsgi.py

${INSTALL_DIR}/venv/bin/python manage.py runmodwsgi --setup-only \
    --port=80 \
    --user www-data --group www-data \
    --server-root=/etc/mod_wsgi-express-80 \
    --settings=signetsim.settings.apache \
    --url-alias /static ${INSTALL_DIR}/static/ \
    --url-alias /media ${INSTALL_DIR}/data/media/ \
    --reload-on-changes


cd $EXEC_DIR
