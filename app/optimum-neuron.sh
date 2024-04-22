#!/bin/bash

pip install --upgrade pip
pip config set global.extra-index-url https://pip.repos.neuron.amazonaws.com
pip install "optimum[neuronx, diffusers]"
optimum-cli export neuron \
  --model stabilityai/stable-diffusion-2-1 \
  --task stable-diffusion \
  --batch_size 1 \
  --height 512 \
  --width 512 \
  --auto_cast matmul \
  --auto_cast_type bf16 \
  sd_neuron_sd_21/

while true; do sleep 1000; done
