#!/bin/bash -x

. aws_neuron_venv_pytorch_inf/bin/activate
time python /compile-neuron-model.py 
deactivate
tar -czvf /sd2_compile_dir_512.tar.gz /sd2_compile_dir_512/
aws s3 cp /sd2_compile_dir_512.tar.gz s3://sdinfer/sd2_compile_dir_512_xla.tar.gz
aws s3api put-object-acl --bucket sdinfer --key sd2_compile_dir_512_xla.tar.gz --acl public-read
