#!/bin/bash -x

tar -xzf /app/model.tar.gz 
pip install --upgrade pip
if [ "$(uname -i)" = "x86_64" ]; then
  if [ $DEVICE="xla" ]; then
    pip install diffusers==0.20.2 transformers==4.33.1 accelerate==0.22.0 safetensors==0.3.1 matplotlib Pillow ipython -U      
  elif [ $DEVICE="cuda" ]; then
    pip install environment_kernels
    pip install diffusers transformers accelerate safetensors matplotlib Pillow ipython torch -U
  fi
  python /run1.py
fi
while true; do sleep 1000; done
