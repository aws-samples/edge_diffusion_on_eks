#!/bin/bash -x

. aws_neuron_venv_pytorch_inf/bin/activate
time python /compile-neuron-model.py
time python /run-neuro-model.py
deactivate
