#!/bin/bash

if [ "$(uname -i)" = "x86_64" ]; then
  # Create Python venv
  python3 -m venv aws_gpu_venv_pytorch

  # Activate Python venv 
  . aws_gpu_venv_pytorch/bin/activate 
  python -m pip install -U pip 
  python -m pip install gradio

  pip install environment_kernels

  # Install python packages
  pip install diffusers transformers accelerate safetensors scipy matplotlib Pillow ipython torch -U
  deactivate
fi
