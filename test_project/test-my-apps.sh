#! /usr/bin/env bash
scriptdir=`dirname "${BASH_SOURCE}"`
python ${scriptdir}/manage.py test -v2 dublincore collection_record
