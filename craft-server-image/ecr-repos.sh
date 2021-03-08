#!/bin/sh

echo "Creating docker image repositories"
aws cloudformation create-stack --stack-name ecr-repos-craft --template-body file://./ecr-repos.json
