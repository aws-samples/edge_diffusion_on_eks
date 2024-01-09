#!/bin/bash -x

tar -xvzf /app/model.tar.gz 

#. aws_${DEVICE}_venv_pytorch/bin/activate
if [[ $MODEL_FILE == "stable-diffusion-2-1-base" ]]; then
  python /sd2_512_benchmark.py
fi
#deactivate
while true; do sleep 1000; done
