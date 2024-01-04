#!/bin/bash -x

. aws_neuron_venv_pytorch_inf/bin/activate
time python /compile-neuron-model.py 
deactivate
tar -czvf /${MODEL_DIR}.tar.gz /${MODEL_DIR}/
aws s3 cp /${MODEL_DIR}.tar.gz s3://sdinfer/{MODEL_DIR}_xla.tar.gz
aws s3api put-object-acl --bucket sdinfer --key {MODEL_DIR}_xla.tar.gz --acl public-read
