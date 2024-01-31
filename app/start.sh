#!/bin/bash -x

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

if [[ $instance_type == "inf"* ]]; then
  echo "export PATH=/opt/aws/neuron/bin:\$PATH" >> /root/.bashrc
  echo "export TERM=screen" >> /root/.bashrc
  echo "export DEVICE=xla" >> /root/.bashrc
fi
if [[ $instance_type == "g"* ]]; then
  echo "export DEVICE=cuda" >> /root/.bashrc
fi
. /root/.bashrc

if [[ $STAGE == "compile" ]]; then
  /compile-model.sh
elif [[ $STAGE == "run" ]]; then
  /run-model.sh
elif [[ $STAGE == "run1" ]]; then
  /run1-model.sh
else
 echo "stage " $STAGE" is not supported"
 exit
fi
