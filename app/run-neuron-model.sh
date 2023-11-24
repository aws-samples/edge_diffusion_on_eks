#!/bin/bash -x

. aws_neuron_venv_pytorch_inf/bin/activate
time python /run-neuron-model.py 
deactivate
