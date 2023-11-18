#!/bin/bash

if [ "$(uname -i)" = "x86_64" ]; then
  # Install kubectl
  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
  install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
  kubectl version --client

  # Install Python venv 
  apt-get install -y python3-venv g++ 

  # Create Python venv
  python -m venv aws_neuron_venv_pytorch_inf 

  # Activate Python venv 
  . aws_neuron_venv_pytorch_inf/bin/activate 

  python -m pip install -U pip 

  # Set pip repository pointing to the Neuron repository 
  python -m pip config set global.extra-index-url https://pip.repos.neuron.amazonaws.com

  # Install wget, awscli
  python -m pip install wget
  python -m pip install awscli
  python -m pip install gradio

  # Install Neuron Compiler and Framework
  python -m pip install neuronx-cc==2.* torch-neuronx torchvision

  # Install model specific packages
  env TOKENIZERS_PARALLELISM=True #Supresses tokenizer warnings making errors easier to detect
  pip install diffusers==0.20.2 transformers==4.33.1 accelerate==0.22.0 safetensors==0.3.1 matplotlib Pillow ipython -U
  deactivate
fi
