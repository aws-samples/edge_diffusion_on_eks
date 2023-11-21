#!/bin/bash -x

#delete the below after validating mulit-stage docker image works
#aws s3 cp s3://sdinfer/sd_1_5_fp32_512_compile_workdir.tar.gz /
#tar -xvf /sd_1_5_fp32_512_compile_workdir.tar.gz

. aws_neuron_venv_pytorch_inf/bin/activate
time python /compile-neuron-model.py 
deactivate
