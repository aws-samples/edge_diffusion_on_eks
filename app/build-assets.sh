#!/bin/bash -x

docker logout
if [ "$IMAGE_TAG" == "amd64-neuron" ]; then
  aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 763104351884.dkr.ecr.us-west-2.amazonaws.com
  docker pull 763104351884.dkr.ecr.us-west-2.amazonaws.com/pytorch-inference-neuronx:1.13.1-neuronx-py310-sdk2.17.0-ubuntu20.04
  dlc_xla_image_id=$(docker images | grep 763104351884 | grep 1.13.1-neuronx-py310-sdk2.17.0-ubuntu20.04 | awk '{print $3}')
  docker tag $dlc_xla_image_id $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$BASE_REPO:1.13.1-neuronx-py310-sdk2.17.0-ubuntu20.04
  docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$BASE_REPO:1.13.1-neuronx-py310-sdk2.17.0-ubuntu20.04
fi
if [ "$IMAGE_TAG" == "amd64-cuda" ]; then
  aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 763104351884.dkr.ecr.us-east-1.amazonaws.com
  docker pull 763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-inference:2.0.1-gpu-py310-cu118-ubuntu20.04-ec2
  dlc_cuda_image_id=$(docker images | grep 763104351884 | grep 2.0.1-gpu-py310-cu118-ubuntu20.04-ec2 | awk '{print $3}')
  docker tag $dlc_cuda_image_id $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$BASE_REPO:2.0.1-gpu-py310-cu118-ubuntu20.04-ec2
  docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$BASE_REPO:2.0.1-gpu-py310-cu118-ubuntu20.04-ec2
fi
docker images

ASSETS="-assets"
export IMAGE=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$BASE_REPO:$IMAGE_TAG$ASSETS
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $IMAGE
docker build -t $IMAGE --build-arg ai_chip=$IMAGE_TAG  -f Dockerfile-assets .
docker push $IMAGE
