#!/bin/bash -x
. /root/.bashrc
python -m venv aws_${DEVICE}_venv_pytorch
if [ "$(uname -i)" = "x86_64" ]; then
  . aws_${DEVICE}_venv_pytorch/bin/activate
  if [ $DEVICE="xla" ]; then
    pip install diffusers==0.20.2 transformers==4.33.1 accelerate==0.22.0 safetensors==0.3.1 matplotlib Pillow ipython -U
  fi
  python /sd2_512_compile.py
  deactivate
fi
tar -czvf /${COMPILER_WORKDIR_ROOT}/${MODEL_FILE}.tar.gz /${COMPILER_WORKDIR_ROOT}/
aws s3 cp /${COMPILER_WORKDIR_ROOT}/${MODEL_FILE}.tar.gz s3://${BUCKET}/${MODEL_FILE}_${DEVICE}.tar.gz
aws s3api put-object-acl --bucket ${BUCKET} --key ${MODEL_FILE}_${DEVICE}.tar.gz --acl public-read
