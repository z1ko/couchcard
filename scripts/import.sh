#!/bin/bash
# Import VeronaCard data into the cluster

for var in "$@"
do
  echo "Importing ${var}" 
  /opt/couchbase/bin/cbimport csv -c http://127.0.0.1 -u admin -p password \
    -d file://$1 \
    -b 'couchcard' --scope-collection-exp 'data.swipes' \
    -g '#UUID#'
done
