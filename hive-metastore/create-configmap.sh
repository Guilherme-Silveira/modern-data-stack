#!/bin/bash


kubectl create secret generic my-s3-keys --from-literal=access-key=silveira --from-literal=secret-key=guilherme@123 --namespace mds
kubectl create configmap metastore-cfg --namespace mds --dry-run=client --from-file=build/metastore-site.xml --from-file=build/core-site.xml -o yaml | kubectl apply -f -
