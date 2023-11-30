#!/bin/bash -x

. aws_neuron_venv_pytorch_gpu/bin/activate
time python ./run-nvidia-model.py 
deactivate
while true; do sleep 1000; done
