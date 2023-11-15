#!/bin/bash -x

cd /home/ubuntu
#install per - https://awsdocs-neuron.readthedocs-hosted.com/en/latest/general/setup/neuron-setup/pytorch/neuronx/ubuntu/torch-neuronx-ubuntu22.html#setup-torch-neuronx-ubuntu22

. /etc/os-release
tee /etc/apt/sources.list.d/neuron.list > /dev/null <<EOF
deb https://apt.repos.neuron.amazonaws.com ${VERSION_CODENAME} main
EOF
wget -qO - https://apt.repos.neuron.amazonaws.com/GPG-PUB-KEY-AMAZON-AWS-NEURON.PUB | apt-key add -
apt-get update -y
apt-get upgrade -y
apt-get dist-upgrade -y
apt-get install linux-headers-$(uname -r) -y
apt-get install git -y
apt-get install aws-neuronx-dkms=2.* -y
apt-get install aws-neuronx-collectives=2.* -y
apt-get install aws-neuronx-runtime-lib=2.* -y
apt-get install aws-neuronx-tools=2.* -y
export PATH=/opt/aws/neuron/bin:$PATH

apt-get install -y python3.10-venv g++ 
python3.10 -m venv aws_neuron_venv_pytorch
. aws_neuron_venv_pytorch/bin/activate
python -m pip install -U pip
pip install ipykernel
python3.10 -m ipykernel install --user --name aws_neuron_venv_pytorch --display-name "Python (torch-neuronx)"
pip install jupyter notebook
pip install environment_kernels
python -m pip config set global.extra-index-url https://pip.repos.neuron.amazonaws.com
python -m pip install wget 
python -m pip install awscli 
python -m pip install neuronx-cc==2.* torch-neuronx torchvision
