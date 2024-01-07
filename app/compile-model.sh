#!/bin/bash -x

. aws_${DEVICE}_venv_pytorch/bin/activate
python /sd2_512_compile.py
deactivate
tar -czvf /sd2_compile_dir/${MODEL_FILE}.tar.gz /sd2_compile_dir/
aws s3 cp /sd2_compile_dir/${MODEL_FILE}.tar.gz s3://${BUCKET}/${MODEL_FILE}_${DEVICE}.tar.gz
aws s3api put-object-acl --bucket ${BUCKET} --key ${MODEL_FILE}_${DEVICE}.tar.gz --acl public-read
