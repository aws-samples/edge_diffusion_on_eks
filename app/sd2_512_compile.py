import os
os.environ["NEURON_FUSE_SOFTMAX"] = "1"
model_id=os.environ['MODEL_ID']
device=os.environ["DEVICE"]
model_dir=os.environ['COMPILER_WORKDIR_ROOT']
from pathlib import Path

import torch
import torch.nn as nn
if device=='xla':
  import torch_neuronx

import copy
from diffusers import StableDiffusionPipeline,DPMSolverMultistepScheduler,EulerAncestralDiscreteScheduler
from diffusers.models.unet_2d_condition import UNet2DConditionOutput
# Compatibility for diffusers<0.18.0
from packaging import version
import diffusers
diffusers_version = version.parse(diffusers.__version__)
use_new_diffusers = diffusers_version >= version.parse('0.18.0')
if use_new_diffusers:
    from diffusers.models.attention_processor import Attention
else:
    from diffusers.models.cross_attention import CrossAttention

# Define datatype
DTYPE = torch.bfloat16

# Have to do this double wrapper trick to compile the unet, because
# of the special UNet2DConditionOutput output type.
class UNetWrap(nn.Module):
    def __init__(self, unet):
        super().__init__()
        self.unet = unet

    def forward(self, sample, timestep, encoder_hidden_states, cross_attention_kwargs=None):
        out_tuple = self.unet(sample, timestep, encoder_hidden_states, return_dict=False)
        return out_tuple

class NeuronUNet(nn.Module):
    def __init__(self, unetwrap):
        super().__init__()
        self.unetwrap = unetwrap
        self.config = unetwrap.unet.config
        self.in_channels = unetwrap.unet.in_channels
        self.device = unetwrap.unet.device

    def forward(self, sample, timestep, encoder_hidden_states, cross_attention_kwargs=None):
        sample = self.unetwrap(sample, timestep.to(dtype=DTYPE).expand((sample.shape[0],)), encoder_hidden_states)[0]
        return UNet2DConditionOutput(sample=sample)
    
class NeuronTextEncoder(nn.Module):
    def __init__(self, text_encoder):
        super().__init__()
        self.neuron_text_encoder = text_encoder
        self.config = text_encoder.config
        self.dtype = text_encoder.dtype
        self.device = text_encoder.device

    def forward(self, emb, attention_mask = None):
        return [self.neuron_text_encoder(emb)['last_hidden_state']]


# Optimized attention
def get_attention_scores(self, query, key, attn_mask):       
    dtype = query.dtype

    if self.upcast_attention:
        query = query.float()
        key = key.float()

    # Check for square matmuls
    if(query.size() == key.size()):
        attention_scores = custom_badbmm(
            key,
            query.transpose(-1, -2)
        )

        if self.upcast_softmax:
            attention_scores = attention_scores.float()

        attention_probs = attention_scores.softmax(dim=1).permute(0,2,1)
        attention_probs = attention_probs.to(dtype)

    else:
        attention_scores = custom_badbmm(
            query,
            key.transpose(-1, -2)
        )

        if self.upcast_softmax:
            attention_scores = attention_scores.float()

        attention_probs = attention_scores.softmax(dim=-1)
        attention_probs = attention_probs.to(dtype)
        
    return attention_probs

# In the original badbmm the bias is all zeros, so only apply scale
def custom_badbmm(a, b):
    bmm = torch.bmm(a, b)
    scaled = bmm * 0.125
    return scaled


# For saving compiler artifacts
COMPILER_WORKDIR_ROOT = 'sd2_compile_dir_512'

# Model ID for SD version pipeline
#model_id = "stabilityai/stable-diffusion-2-1-base"

pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=DTYPE)
if device=='cuda':
  pipe = pipe.to("cuda")
  pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
  pipe.unet.to(memory_format=torch.channels_last)
  pipe.vae.to(memory_format=torch.channels_last)
  pipe.unet = torch.compile(pipe.unet, fullgraph=True, mode="max-autotune")
  unet_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'unet/model.pt')
  torch.save(pipe.unet.state_dict(), unet_filename) 

  pipe.text_encoder = torch.compile(
    pipe.text_encoder,
    fullgraph=True,
    mode="max-autotune",
  )
  text_encoder_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'text_encoder/model.pt')
  torch.save(pipe.text_encoder.state_dict(), text_encoder_filename)
  
  pipe.vae.decoder = torch.compile(
    pipe.vae.decoder,
    fullgraph=True,
    mode="max-autotune",
  )
  decoder_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'vae_decoder/model.pt')
  torch.save(pipe.vae.decoder.state_dict(), decoder_filename)  

  pipe.vae.post_quant_conv = torch.compile(
    pipe.vae.post_quant_conv,
    fullgraph=True,
    mode="max-autotune-no-cudagraphs",
  )
  post_quant_conv_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'vae_post_quant_conv/model.pt')
  torch.save(pipe.vae.post_quant_conv.state_dict(), post_quant_conv_filename)

# --- Compile UNet and save ---
# Replace original cross-attention module with custom cross-attention module for better performance
if use_new_diffusers:
    Attention.get_attention_scores = get_attention_scores
else:
    CrossAttention.get_attention_scores = get_attention_scores

if device=='xla':
  # Apply double wrapper to deal with custom return type
  pipe.unet = NeuronUNet(UNetWrap(pipe.unet))

  # Only keep the model being compiled in RAM to minimze memory pressure
  unet = copy.deepcopy(pipe.unet.unetwrap)
  del pipe

# Compile unet - FP32
sample_1b = torch.randn([1, 4, 64, 64], dtype=DTYPE)
timestep_1b = torch.tensor(999, dtype=DTYPE).expand((1,))
encoder_hidden_states_1b = torch.randn([1, 77, 1024], dtype=DTYPE)
example_inputs = sample_1b, timestep_1b, encoder_hidden_states_1b

if device=='xla':
  unet_neuron = torch_neuronx.trace(
    unet,
    example_inputs,
    compiler_workdir=os.path.join(COMPILER_WORKDIR_ROOT, 'unet'),
    compiler_args=["--model-type=unet-inference", "--enable-fast-loading-neuron-binaries"]
  )

  # Enable asynchronous and lazy loading to speed up model load
  torch_neuronx.async_load(unet_neuron)
  torch_neuronx.lazy_load(unet_neuron)

  # save compiled unet
  unet_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'unet/model.pt')
  torch.jit.save(unet_neuron, unet_filename)

  # delete unused objects
  del unet
  del unet_neuron

# --- Compile CLIP text encoder and save ---

# Only keep the model being compiled in RAM to minimze memory pressure
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=DTYPE)
text_encoder = copy.deepcopy(pipe.text_encoder)
del pipe

if device=='xla':
  # Apply the wrapper to deal with custom return type
  text_encoder = NeuronTextEncoder(text_encoder)

# Compile text encoder
# This is used for indexing a lookup table in torch.nn.Embedding,
# so using random numbers may give errors (out of range).
emb = torch.tensor([[49406, 18376,   525,  7496, 49407,     0,     0,     0,     0,     0,
        0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
        0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
        0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
        0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
        0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
        0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
        0,     0,     0,     0,     0,     0,     0]])

if device=='xla':
  text_encoder_neuron = torch_neuronx.trace(
        text_encoder.neuron_text_encoder, 
        emb, 
        compiler_workdir=os.path.join(COMPILER_WORKDIR_ROOT, 'text_encoder'),
        compiler_args=["--enable-fast-loading-neuron-binaries"]
        )

  # Enable asynchronous loading to speed up model load
  torch_neuronx.async_load(text_encoder_neuron)

  # Save the compiled text encoder
  text_encoder_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'text_encoder/model.pt')
  torch.jit.save(text_encoder_neuron, text_encoder_filename)

  # delete unused objects
  del text_encoder
  del text_encoder_neuron

# --- Compile VAE decoder and save ---

# Only keep the model being compiled in RAM to minimze memory pressure
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)
decoder = copy.deepcopy(pipe.vae.decoder)
del pipe

# Compile vae decoder
decoder_in = torch.randn([1, 4, 64, 64], dtype=torch.float32)
if device=='xla':
  decoder_neuron = torch_neuronx.trace(
    decoder, 
    decoder_in, 
    compiler_workdir=os.path.join(COMPILER_WORKDIR_ROOT, 'vae_decoder'),
    compiler_args=["--enable-fast-loading-neuron-binaries"]
  )

  # Enable asynchronous loading to speed up model load
  torch_neuronx.async_load(decoder_neuron)

  # Save the compiled vae decoder
  decoder_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'vae_decoder/model.pt')
  torch.jit.save(decoder_neuron, decoder_filename)

  # delete unused objects
  del decoder
  del decoder_neuron

# --- Compile VAE post_quant_conv and save ---

# Only keep the model being compiled in RAM to minimze memory pressure
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)
post_quant_conv = copy.deepcopy(pipe.vae.post_quant_conv)
del pipe

# # Compile vae post_quant_conv
post_quant_conv_in = torch.randn([1, 4, 64, 64], dtype=torch.float32)
if device=='xla':
  post_quant_conv_neuron = torch_neuronx.trace(
    post_quant_conv, 
    post_quant_conv_in,
    compiler_workdir=os.path.join(COMPILER_WORKDIR_ROOT, 'vae_post_quant_conv'),
  )

  # Enable asynchronous loading to speed up model load
  torch_neuronx.async_load(post_quant_conv_neuron)

  # # Save the compiled vae post_quant_conv
  post_quant_conv_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'vae_post_quant_conv/model.pt')
  torch.jit.save(post_quant_conv_neuron, post_quant_conv_filename)

  # delete unused objects
  del post_quant_conv
  del post_quant_conv_neuron

