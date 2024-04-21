#!/bin/bash

pip install --upgrade pip
pip config set global.extra-index-url https://pip.repos.neuron.amazonaws.com
pip install --upgrade-strategy eager optimum[neuronx]
optimum-cli export neuron \
  --model distilbert-base-uncased-finetuned-sst-2-english \
  --batch_size 1 \
  --sequence_length 32 \
  --auto_cast matmul \
  --auto_cast_type bf16 \
  distilbert_base_uncased_finetuned_sst2_english_neuron/

while true; do sleep 1000; done
