#!/bin/bash -x

tar -xzf /app/model.tar.gz 
python -m venv aws_${DEVICE}_venv_pytorch
if [ "$(uname -i)" = "x86_64" ]; then
  . aws_${DEVICE}_venv_pytorch/bin/activate
  pip install --upgrade pip
  if [ $DEVICE="xla" ]; then
    pip install diffusers==0.20.2 transformers==4.33.1 accelerate==0.22.0 safetensors==0.3.1 matplotlib Pillow ipython -U      
  fi
  python /sd2_512_benchmark.py
  deactivate
fi
while true; do sleep 1000; done
