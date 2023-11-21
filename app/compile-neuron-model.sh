#!/bin/bash -x

#delete the below after validating mulit-stage docker image works
#aws s3 cp s3://sdinfer/sd_1_5_fp32_512_compile_workdir.tar.gz /

. aws_neuron_venv_pytorch_inf/bin/activate
time python /compile-neuron-model.py 
deactivate
tar -czvf /sd_1_5_fp32_512_compile_workdir.tar.gz /sd_1_5_fp32_512_compile_workdir/
aws s3 cp /sd_1_5_fp32_512_compile_workdir.tar.gz s3://sdinfer/sd_1_5_fp32_512_compile_workdir.tar.gz
