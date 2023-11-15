#!/bin/bash -x
PIP_REPO=https://pip.repos.neuron.amazonaws.com
PIP="pip"
if [ "$(uname -i)" = "x86_64" ]; then
  ${PIP} config set global.extra-index-url $PIP_REPO 
  ${PIP} install --force-reinstall neuronx-cc torch-neuronx torchvision --extra-index-url $PIP_REPO --break-system-packages
fi
