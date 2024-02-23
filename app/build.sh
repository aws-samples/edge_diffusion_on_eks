#!/bin/bash -x

docker logout
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 763104351884.dkr.ecr.us-west-2.amazonaws.com
docker pull 763104351884.dkr.ecr.us-west-2.amazonaws.com/pytorch-inference-neuronx:1.13.1-neuronx-py310-sdk2.17.0-ubuntu20.04
dlc_xla_image_id=$(docker images | grep 763104351884 | grep 1.13.1-neuronx-py310-sdk2.17.0-ubuntu20.04 | awk '{print $3}')
docker logout
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 763104351884.dkr.ecr.us-east-1.amazonaws.com
docker pull 763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-inference:2.0.1-gpu-py310-cu118-ubuntu20.04-ec2
dlc_cuda_image_id=$(docker images | grep 763104351884 | grep 2.0.1-gpu-py310-cu118-ubuntu20.04-ec2 | awk '{print $3}')
docker images
docker logout

export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --output text --query Account)

ASSETS="-assets"
export BASE_IMAGE=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$BASE_REPO:$BASE_IMAGE_TAG
export ASSETS_IMAGE=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$BASE_REPO:$IMAGE_TAG$ASSETS
export IMAGE=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$BASE_REPO:$IMAGE_TAG

if [ "$IMAGE_TAG" == "1.13.1-neuronx-py310-sdk2.17.0-ubuntu20.04" ]; then
  docker tag $dlc_xla_image_id $BASE_IMAGE
fi
if [ "$IMAGE_TAG" == "2.0.1-gpu-py310-cu118-ubuntu20.04-ec2" ]; then
  docker tag $dlc_cuda_image_id $BASE_IMAGE
fi
docker images

cat Dockerfile.template | envsubst > Dockerfile
cat Dockerfile
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $BASE_IMAGE
docker build -t $IMAGE .
docker push $IMAGE
