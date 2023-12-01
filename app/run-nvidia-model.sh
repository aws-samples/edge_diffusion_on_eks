#!/bin/bash -x

. aws_gpu_venv_pytorch/bin/activate
time python /run-nvidia-model.py 
deactivate
while true; do sleep 1000; done
