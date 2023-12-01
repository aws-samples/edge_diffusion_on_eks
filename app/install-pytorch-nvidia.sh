#!/bin/bash

if [ "$(uname -i)" = "x86_64" ]; then
  # Install Python venv 
  apt-get install -y python3-venv g++
  #apt-get install -y gettext-base

  # Create Python venv
  python3 -m venv aws_gpu_venv_pytorch

  # Activate Python venv 
  . aws_gpu_venv_pytorch/bin/activate 
  python -m pip install -U pip 
  python -m pip install gradio

  # Install Jupyter notebook kernel
  pip install ipykernel 
  python3 -m ipykernel install --user --name aws_gpu_venv_pytorch --display-name "Python (torch-nvidia)"
  pip install jupyter notebook
  pip install environment_kernels

  # Install PyTorch 
  pip install diffusers==0.20.2 transformers==4.33.1 accelerate==0.22.0 safetensors==0.3.1 matplotlib Pillow ipython torch -U
  deactivate
fi
