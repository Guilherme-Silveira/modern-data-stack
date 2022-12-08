#!/bin/bash

helm repo add minio https://charts.min.io/
helm repo update
helm install minio --namespace mds -f values.yaml minio/minio