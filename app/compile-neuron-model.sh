#!/bin/bash -x

. aws_neuron_venv_pytorch_inf/bin/activate
time python /compile-neuron-model.py 
deactivate
tar -czvf /sd2_compile_dir/${MODEL_FILE}.tar.gz /sd2_compile_dir/
aws s3 cp /sd2_compile_dir/${MODEL_FILE}.tar.gz s3://sdinfer/{MODEL_FILE}_xla.tar.gz
aws s3api put-object-acl --bucket sdinfer --key /{MODEL_FILE}_xla.tar.gz --acl public-read
