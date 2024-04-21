#!/bin/bash

pip install --upgrade pip
pip config set global.extra-index-url https://pip.repos.neuron.amazonaws.com
pip install "optimum[neuronx, diffusers]"
optimum-cli export neuron \
  --model $MODEL_ID \
  --task stable-diffusion \
  --batch_size $BATCH_SIZE \
  --height $HEIGHT \
  --width $WIDTH \
  --auto_cast matmul \
  --auto_cast_type bf16 \
  $COMPILER_WORKDIR_ROOT/
