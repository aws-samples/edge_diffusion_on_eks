#!/bin/bash

source account.conf
repo='.dkr.ecr.us-west-2.amazonaws.com/game-server-init-container:latest'
repo_url=$account$repo

$(aws ecr get-login --no-include-email --region us-west-2)
docker build -t game-server-init-container .
docker tag game-server-init-container:latest $repo_url
docker push $repo_url
