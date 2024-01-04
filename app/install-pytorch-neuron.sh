#!/bin/bash

if [ "$(uname -i)" = "x86_64" ]; then
  # Create Python venv
  python -m venv aws_neuron_venv_pytorch_inf 

  # Activate Python venv 
  . aws_neuron_venv_pytorch_inf/bin/activate 

  python -m pip install -U pip 
  python -m pip install gradio

  # Set pip repository pointing to the Neuron repository 
  python -m pip config set global.extra-index-url https://pip.repos.neuron.amazonaws.com

  # Install Neuron Compiler and Framework
  python -m pip install neuronx-cc==2.* torch-neuronx torchvision

  # Install model specific packages
  env TOKENIZERS_PARALLELISM=True #Supresses tokenizer warnings making errors easier to detect
  pip install diffusers==0.20.2 transformers==4.33.1 accelerate==0.22.0 safetensors==0.3.1 scipy matplotlib Pillow ipython -U
  #pip install diffusers transformers accelerate safetensors scipy matplotlib Pillow ipython torch -U
  deactivate
fi
