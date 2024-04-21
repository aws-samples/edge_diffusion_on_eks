#!/bin/bash

pip install --upgrade pip
pip config set global.extra-index-url https://pip.repos.neuron.amazonaws.com
pip install "optimum[neuronx, diffusers]"
pip uninstall awscli -y
pip uninstall botocore s3transfer -y
pip install awscli
optimum-cli export neuron \
  --model $MODEL_ID \
  --task stable-diffusion \
  --batch_size $BATCH_SIZE \
  --height $HEIGHT \
  --width $WIDTH \
  --auto_cast matmul \
  --auto_cast_type bf16 \
  $COMPILER_WORKDIR_ROOT/
