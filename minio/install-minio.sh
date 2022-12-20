#!/bin/bash

helm repo add minio https://charts.min.io/
helm repo update
helm install minio --version 5.0.3 --namespace mds -f values.yaml minio/minio