#!/bin/bash

# Remove old bucket if present

curl -v -X DELETE -u admin:password \
  http://127.0.0.1:8091/pools/default/buckets/couchcard

# Create a new bucket on the cluster

curl -v -X POST http://127.0.0.1:8091/pools/default/buckets \
  -u admin:password \
  -d name=couchcard \
  -d bucketType=couchbase \
  -d ramQuota=4025

# Create the data and import scopes

curl -v -X POST http://127.0.0.1:8091/pools/default/buckets/couchcard/scopes \
  -u admin:password \
  -d name=data

# Create the collections

curl -v -X POST http://127.0.0.1:8091/pools/default/buckets/couchcard/scopes/data/collections \
  -u admin:password \
  -d name=swipes

curl -v -X POST http://127.0.0.1:8091/pools/default/buckets/couchcard/scopes/data/collections \
  -u admin:password \
  -d name=pois

curl -v -X POST http://127.0.0.1:8091/pools/default/buckets/couchcard/scopes/data/collections \
  -u admin:password \
  -d name=cards

curl -v -X POST http://127.0.0.1:8091/pools/default/buckets/couchcard/scopes/data/collections \
  -u admin:password \
  -d name=days
