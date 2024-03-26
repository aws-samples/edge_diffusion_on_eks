import os
os.environ["NEURON_FUSE_SOFTMAX"] = "1"
pod_name=os.environ['POD_NAME']
model_id=os.environ['MODEL_ID']
device=os.environ["DEVICE"]
model_dir=os.environ['COMPILER_WORKDIR_ROOT']
number_of_runs_per_inference=os.environ['NUM_OF_RUNS_INF']
import gradio as gr
from fastapi import FastAPI
import random
from matplotlib import image as mpimg
from matplotlib import pyplot as plt
import torch
import torch.nn as nn
if device=='xla':
  import torch_neuronx

from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from diffusers.models.unet_2d_condition import UNet2DConditionOutput

import time
import math

# Define datatype
DTYPE = torch.bfloat16

# Specialized benchmarking class for stable diffusion.
# We cannot use any of the pre-existing benchmarking utilities to benchmark E2E stable diffusion performance,
# because the top-level StableDiffusionPipeline cannot be serialized into a single Torchscript object.
# All of the pre-existing benchmarking utilities (in neuronperf or torch_neuronx) require the model to be a
# traced Torchscript.
def benchmark(n_runs, test_name, model, model_inputs):
    if not isinstance(model_inputs, tuple):
        model_inputs = (model_inputs,)
    
    warmup_run = model(*model_inputs)

    latency_collector = LatencyCollector()
    # can't use register_forward_pre_hook or register_forward_hook because StableDiffusionPipeline is not a torch.nn.Module
    
    for _ in range(n_runs):
        latency_collector.pre_hook()
        res = model(*model_inputs)
        latency_collector.hook()
    
    p0_latency_ms = latency_collector.percentile(0) * 1000
    p50_latency_ms = latency_collector.percentile(50) * 1000
    p90_latency_ms = latency_collector.percentile(90) * 1000
    p95_latency_ms = latency_collector.percentile(95) * 1000
    p99_latency_ms = latency_collector.percentile(99) * 1000
    p100_latency_ms = latency_collector.percentile(100) * 1000

    report_dict = dict()
    report_dict["Latency P0"] = f'{p0_latency_ms:.1f}'
    report_dict["Latency P50"]=f'{p50_latency_ms:.1f}'
    report_dict["Latency P90"]=f'{p90_latency_ms:.1f}'
    report_dict["Latency P95"]=f'{p95_latency_ms:.1f}'
    report_dict["Latency P99"]=f'{p99_latency_ms:.1f}'
    report_dict["Latency P100"]=f'{p100_latency_ms:.1f}'

    report = f'RESULT FOR {test_name}:'
    for key, value in report_dict.items():
        report += f' {key}={value}'
    print(report)
    return report

class LatencyCollector:
    def __init__(self):
        self.start = None
        self.latency_list = []

    def pre_hook(self, *args):
        self.start = time.time()

    def hook(self, *args):
        self.latency_list.append(time.time() - self.start)

    def percentile(self, percent):
        latency_list = self.latency_list
        pos_float = len(latency_list) * percent / 100
        max_pos = len(latency_list) - 1
        pos_floor = min(math.floor(pos_float), max_pos)
        pos_ceil = min(math.ceil(pos_float), max_pos)
        latency_list = sorted(latency_list)
        return latency_list[pos_ceil] if pos_float - pos_floor > 0.5 else latency_list[pos_floor]


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

    def forward(self, sample, timestep, encoder_hidden_states, cross_attention_kwargs=None, return_dict=False):
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
    
def decode_latents(self, latents):
    latents = latents.to(torch.float)
    latents = 1 / self.vae.config.scaling_factor * latents
    image = self.vae.decode(latents).sample
    image = (image / 2 + 0.5).clamp(0, 1)
    image = image.cpu().permute(0, 2, 3, 1).float().numpy()
    return image

StableDiffusionPipeline.decode_latents = decode_latents

# --- Load all compiled models and benchmark pipeline ---
COMPILER_WORKDIR_ROOT = model_dir
#model_id = "stabilityai/stable-diffusion-2-1-base"
text_encoder_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'text_encoder/model.pt')
decoder_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'vae_decoder/model.pt')
unet_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'unet/model.pt')
post_quant_conv_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'vae_post_quant_conv/model.pt')

pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=DTYPE)
if device=='cuda':
  pipe = pipe.to("cuda")

pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

if device=='xla':
  # Load the compiled UNet onto two neuron cores.
  pipe.unet = NeuronUNet(UNetWrap(pipe.unet))
  device_ids = [0,1]
  pipe.unet.unetwrap = torch_neuronx.DataParallel(torch.jit.load(unet_filename), device_ids, set_dynamic_batching=False)

class NeuronTypeConversionWrapper(nn.Module):
    def __init__(self, network):
        super().__init__()
        self.network = network

    def forward(self, x):
        return self.network(x.float())

if device=='xla':
  # Load other compiled models onto a single neuron core.
  pipe.text_encoder = NeuronTextEncoder(pipe.text_encoder)
  pipe.text_encoder.neuron_text_encoder = torch.jit.load(text_encoder_filename)
  pipe.vae.decoder = NeuronTypeConversionWrapper(torch.jit.load(decoder_filename))
  pipe.vae.post_quant_conv = NeuronTypeConversionWrapper(torch.jit.load(post_quant_conv_filename))

prompt = "a photo of an astronaut riding a horse on mars"
n_runs = number_of_runs_per_inference
#benchmark(n_runs, "stable_diffusion_512", pipe, prompt)

def text2img(PROMPT):
  start_time = time.time()
  image = pipe(PROMPT).images[0]
  total_time =  time.time()-start_time
  r1 = random.randint(0,99999)
  imgname="image"+str(r1)+".png"
  image.save(imgname)
  image = mpimg.imread(imgname)
  return image, str(total_time)

app = FastAPI()
io = gr.Interface(fn=text2img,inputs=["text"],
    outputs = [gr.Image(height=512, width=512), "text"],
    title = 'Stable Diffusion 2.1 pod ' + pod_name + ' in AWS EC2 ' + device + ' instance')
@app.get("/")
def read_main():
  return {"message": "This is Stable Diffusion 2.1 pod " + pod_name + " in AWS EC2 " + device + " instance; try /load/{n_runs} or /serve"}
@app.get("/load/{n_runs}")
def load(n_runs: int):
  prompt = "a photo of an astronaut riding a horse on mars"
  #n_runs = 20
  report=benchmark(n_runs, "stable_diffusion_512", pipe, prompt)
  return {"message": "benchmark report:"+report}
@app.get("/health")
def healthy():
  return {"message": pod_name + "is healthy"}
@app.get("/readiness")
def ready():
  return {"message": pod_name + "is ready"}
app = gr.mount_gradio_app(app, io, path="/serve")
