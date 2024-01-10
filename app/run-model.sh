#!/bin/bash -x

tar -xzf /app/model.tar.gz 

if [ "$(uname -i)" = "x86_64" ]; then
  if [ $DEVICE="xla" ]; then
    pip install diffusers==0.20.2 transformers==4.33.1 accelerate==0.22.0 safetensors==0.3.1 matplotlib Pillow ipython -U      
    python /sd2_512_benchmark.py
  fi
fi
#. aws_${DEVICE}_venv_pytorch/bin/activate
#if [[ $MODEL_FILE == "stable-diffusion-2-1-base" ]]; then
#deactivate
while true; do sleep 1000; done
