#!/bin/bash -x

export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/cuda/lib64"
export PATH="$PATH:/usr/local/cuda/bin"
export CUDA_HOME="$CUDA_HOME:/usr/local/cuda"

apt-get update -y && apt-get install -y wget linux-aws

if [ "$(uname -i)" = "x86_64" ]; then
  wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-wsl-ubuntu-keyring.gpg 
  mv cuda-wsl-ubuntu-keyring.gpg /usr/share/keyrings/cuda-wsl-ubuntu-keyring.gpg 
  echo "deb [signed-by=/usr/share/keyrings/cuda-wsl-ubuntu-keyring.gpg] https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/ /" | tee /etc/apt/sources.list.d/cuda-wsl-ubuntu-x86_64.list 
  wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-wsl-ubuntu.pin 
  mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600
  apt-get update -y && apt-get install -y cuda nvidia-cuda-toolkit
fi
if [ "$(uname -i)" = "aarch64" ]; then
  wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/cross-linux-sbsa/cuda-archive-keyring.gpg
  mv cuda-archive-keyring.gpg /usr/share/keyrings/
  echo "deb [signed-by=/usr/share/keyrings/cuda-archive-keyring.gpg] https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/cross-linux-sbsa/ /" | tee /etc/apt/sources.list.d/cuda-wsl-ubuntu-arm64.list 
  wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/cross-linux-sbsa/cuda-ubuntu2204.pin
  mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
  echo apt-get update -y && apt-get install -y cuda
fi
