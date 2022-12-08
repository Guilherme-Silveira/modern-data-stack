#!/bin/bash

TABLE_FORMAT=$1

docker run --rm -it --network=host --mount type=bind,source=${PWD}/profiles_${TABLE_FORMAT}.yml,target=/root/.dbt/profiles.yml --mount type=bind,source=${PWD}/jaffle_shop_${TABLE_FORMAT}/,target=/usr/app/ --entrypoint bash guisilveira/dbt-trino