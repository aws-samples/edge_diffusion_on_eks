#!/bin/bash

if [ "$(uname -i)" = "x86_64" ]; then
  # Install Python venv 
  apt-get install -y python3.10-venv g++ 

  # Create Python venv
  python3.10 -m venv aws_neuron_venv_pytorch_gpu

  # Activate Python venv 
  . aws_neuron_venv_pytorch_gpu/bin/activate 
  python -m pip install -U pip 

  # Install Jupyter notebook kernel
  pip install ipykernel 
  python3.10 -m ipykernel install --user --name aws_neuron_venv_pytorch_gpu --display-name "Python (torch-nvidia)"
  pip install jupyter notebook
  pip install environment_kernels

  # Install PyTorch Neuron
  #python -m pip install torch-neuron neuron-cc[tensorflow] "protobuf" torchvision
  pip install -r requirements.txt
  deactivate
fi
