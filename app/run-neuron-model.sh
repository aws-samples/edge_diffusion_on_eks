#!/bin/bash -x

. aws_neuron_venv_pytorch_inf/bin/activate
if [[ $MODEL_FILE == "stable-diffusion-2-1-base" ]]; then
  python /run-sd21-neuron-model.py
fi
deactivate
while true; do sleep 1000; done
