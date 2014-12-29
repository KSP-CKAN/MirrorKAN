#!/bin/sh

. /opt/mono/env.sh

HERE=/home/ckan


mkdir -p ${HERE}/CKAN

cp ${HERE}/Dropbox/ckan/*.exe ${HERE}/CKAN

if [ -d ${HERE}/MirrorKAN.x ]
then
    rm -f ${HERE}/MirrorKAN.x/mirrorkan_conf.py
    ln -sf ${HERE}/MirrorKAN.munich/mirrorkan_conf_SCANsat_pre.py ${HERE}/MirrorKAN.x/mirrorkan_conf.py
fi


THINGS=""
THINGS="${THINGS} --clean"
THINGS="${THINGS} --update-netkan"
THINGS="${THINGS} --push-ckan-meta"
THINGS="${THINGS} --update-mirrorkan"
THINGS="${THINGS} --generate-index"
THINGS="${THINGS} --generate-api"
THINGS="${THINGS} --generate-feed"
THINGS="${THINGS} "

python ${HERE}/MirrorKAN.x/generate_scripts.py ${THINGS} | sh
