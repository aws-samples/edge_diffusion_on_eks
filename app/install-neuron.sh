#!/bin/bash -x
APT_REPO=https://apt.repos.neuron.amazonaws.com

echo "deb $APT_REPO focal main" > /etc/apt/sources.list.d/neuron.list
wget -qO - $APT_REPO/GPG-PUB-KEY-AMAZON-AWS-NEURON.PUB | apt-key add -

apt-get update 
if apt-cache show aws-neuronx-tools &>/dev/null; then 
   apt-get install -y aws-neuronx-tools aws-neuronx-collectives aws-neuronx-runtime-lib 
fi 
rm -rf /var/lib/apt/lists/* 
rm -rf /tmp/tmp* 
apt-get clean
