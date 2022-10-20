#!/bin/bash
# Import VeronaCard data into the cluster

for var in "$@"
do
  echo "Importing ${var}"
  /opt/couchbase/bin/cbimport csv -c http://127.0.0.1:3777 -u admin -p password \
    -d file://$1 \
    -b 'Couchcard' --scope-collection-exp 'import.swipes' \
    -g '#UUID#'
done
