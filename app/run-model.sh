#!/bin/bash -x
pip install --upgrade pip
if [ "$(uname -i)" = "x86_64" ]; then
  if [ "$DEVICE" == "xla" ]; then
    #pip config set global.extra-index-url https://pip.repos.neuron.amazonaws.com
    pip install "optimum[neuronx, diffusers]"
    #pip install diffusers==0.20.2 transformers==4.33.1 accelerate==0.22.0 safetensors==0.3.1 matplotlib Pillow ipython -U      
    #pip install click
    #pip install /diffusion_benchmarker-0.0.1.tar.gz 
    #diffusion_benchmarker t2i --pipeline neuronx_t2i root=/app/sd2_compile_dir_512 pretrained_model_name_or_path=stabilityai/stable-diffusion-2-1 torch_dtype=bfloat16
  elif [ "$DEVICE" == "cuda" ]; then
    pip install environment_kernels
    pip install diffusers transformers accelerate safetensors matplotlib Pillow ipython torch -U
    pip install click nvitop
    #pip install /diffusion_benchmarker-0.0.1.tar.gz 
    #diffusion_benchmarker t2i --pipeline inductor_t2i pretrained_model_name_or_path=stabilityai/stable-diffusion-2-1 torch_dtype=bfloat16
  fi
  #uvicorn run:app --host=0.0.0.0
  uvicorn run-sd2:app --host=0.0.0.0
fi
#while true; do sleep 1000; done
