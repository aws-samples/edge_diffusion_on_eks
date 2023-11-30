#!/bin/bash 

STAGE=$1

token=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
if [ -z "$token" ]; then
  echo "No token for IMDS_v2 - check /api/token url"
  exit
fi
instance_type=$(curl -s -H "X-aws-ec2-metadata-token: $token" 169.254.169.254/latest/meta-data/instance-type)
if [ -z "$instance_type" ]; then
  echo "cant find the instance type. cant continue"
  exit
fi
echo "instance_type="$instance_type

if [[ $instance_type == *"$SUPPORTED_INSTANCES"* ]]; then
  echo $instance_type" is supported"
else
  echo $instance_type" is not supported, please use one of the instances in "$supported_instances
  exit
fi
if [[ $instance_type == "inf2."* ]]; then
  echo "export PATH=/opt/aws/neuron/bin:\$PATH" >> /root/.bashrc
  echo "export TERM=screen" >> /root/.bashrc
  . /root/.bashrc
  time /install-pytorch-neuron.sh
  if [[ $STAGE == "compile" ]]; then
    time /compile-neuron-model.sh
  elif [[ $STAGE == "run" ]]; then
    time /run-neuron-model.sh
  else
    echo "stage " $STAGE" is not supported"
    exit
  fi
elif [[ $instance_type == "g5."* ]]; then
  time /install-pytorch-nvidia.sh
  time /run-nvidia-model.sh
else
  echo $instance_type" is not supported"
  exit
fi

#while true; do sleep 1000; done
