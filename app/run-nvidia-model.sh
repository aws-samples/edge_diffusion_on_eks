#!/bin/bash -x

. aws_neuron_venv_pytorch_gpu/bin/activate
<<<<<<< HEAD
time python /run-nvidia-model.py 
=======
time python ./run-nvidia-model.py 
>>>>>>> 9c0aef2cf13ca5152485715bad94ee5f7f5cf590
deactivate
while true; do sleep 1000; done
