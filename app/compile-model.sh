#!/bin/bash -x
. /root/.bashrc
pip install --upgrade pip
if [ "$(uname -i)" = "x86_64" ]; then
  if [ $DEVICE="xla" ]; then
    /optimum-neuron-sd2-compile.sh 
  fi
fi
tar -czvf /${COMPILER_WORKDIR_ROOT}/${MODEL_FILE}.tar.gz /${COMPILER_WORKDIR_ROOT}/
aws s3 cp /${COMPILER_WORKDIR_ROOT}/${MODEL_FILE}.tar.gz s3://${BUCKET}/${MODEL_FILE}_${DEVICE}_bsize_${BATCH_SIZE}.tar.gz
while true; do sleep 1000; done
