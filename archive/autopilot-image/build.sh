#!/bin/bash

source account.conf
repo='.dkr.ecr.us-west-2.amazonaws.com/autopilot:latest'
repo_url=$account$repo

$(aws ecr get-login --no-include-email --region us-west-2)
docker build -t autopilot .
docker tag autopilot:latest $repo_url
docker push $repo_url
