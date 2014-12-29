#! /bin/sh

HERE=/home/ckan

wget -q -O /tmp/netkan.exe http://ci.ksp-ckan.org:8080/job/NetKAN/lastSuccessfulBuild/artifact/netkan.exe

cmp ${HERE}/Dropbox/ckan/netkan.exe /tmp/netkan.exe >/dev/null 2>/dev/null
if [ "$?" == "1" ]
then
    echo "New binary"
    ls -l /tmp/netkan.exe
    ls -l ${HERE}/Dropbox/ckan/netkan.exe
    cp /tmp/netkan.exe ${HERE}/Dropbox/ckan/netkan.exe
fi

