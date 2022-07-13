#!/bin/bash

echo -n '[worker] Melchior:  '
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' couchcard_melchior_1

echo -n '[worker] Balthasar: '
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' couchcard_balthasar_1

echo -n '[master] Casper:    '
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' couchcard_casper_1