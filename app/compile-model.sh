#!/bin/bash -x
. /root/.bashrc
. aws_${DEVICE}_venv_pytorch/bin/activate
python /sd2_512_compile.py
deactivate
tar -czvf /${COMPILER_WORKDIR_ROOT}/${MODEL_FILE}.tar.gz /${COMPILER_WORKDIR_ROOT}/
aws s3 cp /${COMPILER_WORKDIR_ROOT}/${MODEL_FILE}.tar.gz s3://${BUCKET}/${MODEL_FILE}_${DEVICE}.tar.gz
aws s3api put-object-acl --bucket ${BUCKET} --key ${MODEL_FILE}_${DEVICE}.tar.gz --acl public-read
