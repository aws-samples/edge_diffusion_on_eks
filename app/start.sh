#!/bin/bash 

cd /

if [ -z "$SUPPORTED_INSTANCES" ]; then
  echo "need to know what instances are supported"
  echo "example export SUPPORTED_INSTANCES=trn1n.32xlarge,g5.16xlarge"
  exit
fi

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

#if [[ $instance_type == *"$SUPPORTED_INSTANCES"* ]]; then
#  echo $instance_type" is supported"
#else
#  echo $instance_type" is not supported, please use one of the instances in "$supported_instances
#  exit
#fi
if [[ $instance_type == "trn1n.32xlarge" ]]; then
  echo "export PATH=/opt/aws/neuron/bin:\$PATH" >> /root/.bashrc
  echo "export TERM=screen" >> /root/.bashrc
  . /root/.bashrc
  time /install-pytorch-neuron.sh
elif [[ $instance_type == "g5.xlarge" ]]; then
  time /install-pytorch-nvidia.sh
else
  echo $instance_type" is not supported"
  exit
fi

while true; do sleep 1000; done
