#!/bin/bash -x

export BASE_IMAGE=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$BASE_REPO:$BASE_IMAGE_TAG
export IMAGE=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$BASE_REPO:$IMAGE_TAG
cat Dockerfile.template | envsubst > Dockerfile
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $BASE_IMAGE
docker build -t $IMAGE .
docker push $IMAGE
