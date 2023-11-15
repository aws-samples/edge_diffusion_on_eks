#!/bin/bash -x

if [ "$(uname -i)" = "x86_64" ]; then
  # Configure Linux for Neuron repository updates
  . /etc/os-release
  tee /etc/apt/sources.list.d/neuron.list > /dev/null <<EOF
  deb https://apt.repos.neuron.amazonaws.com ${VERSION_CODENAME} main
EOF
  wget -qO - https://apt.repos.neuron.amazonaws.com/GPG-PUB-KEY-AMAZON-AWS-NEURON.PUB | apt-key add -

  # Update OS packages 
  apt-get update -y

  # Install git 
  echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
  apt-get install python3-dev python3-full jq git -y -q

  # install Neuron Driver
  apt-get install aws-neuronx-dkms=2.* -y

  # Install Neuron Tools 
  apt-get install aws-neuronx-tools=2.* -y

  # Add PATH
  export PATH=/opt/aws/neuron/bin:$PATH
fi
