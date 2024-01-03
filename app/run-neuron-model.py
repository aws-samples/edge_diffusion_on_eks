print("import",flush=True)
import random
import os
os.environ["NEURON_FUSE_SOFTMAX"] = "1"

import torch
import torch.nn as nn
import torch_neuronx
import numpy as np

from matplotlib import pyplot as plt
from matplotlib import image as mpimg
import time
import copy
from IPython.display import clear_output

#from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
from diffusers.models.unet_2d_condition import UNet2DConditionOutput

import gradio as gr

from transformers import CLIPSegProcessor, CLIPSegForImageSegmentation

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

clear_output(wait=False)

print("Define utility classes and functions",flush=True)

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

def custom_badbmm(a, b):
    bmm = torch.bmm(a, b)
    scaled = bmm * 0.125
    return scaled

def decode_latents(self, latents):
    # latents = latents.to(torch.float)
    latents = 1 / self.vae.config.scaling_factor * latents
    image = self.vae.decode(latents).sample
    image = (image / 2 + 0.5).clamp(0, 1)
    image = image.cpu().permute(0, 2, 3, 1).float().numpy()
    return image


print("Load the saved model and run itimport",flush=True)
# --- Load all compiled models ---
COMPILER_WORKDIR_ROOT = 'sd2inpaint_compile_dir'
#model_id = "stabilityai/stable-diffusion-2-1-base"
model_id = "stabilityai/stable-diffusion-2-inpainting"
text_encoder_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'text_encoder/model.pt')
decoder_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'vae_decoder/model.pt')
unet_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'unet/model.pt')
post_quant_conv_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'vae_post_quant_conv/model.pt')

#pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=DTYPE)
pipe = DiffusionPipeline.from_pretrained(model_id, torch_dtype=DTYPE)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

# Replaces StableDiffusionPipeline's decode_latents method with our custom decode_latents method defined above.
#StableDiffusionPipeline.decode_latents = decode_latents
DiffusionPipeline.decode_latents = decode_latents

# Load the compiled UNet onto two neuron cores.
pipe.unet = NeuronUNet(UNetWrap(pipe.unet))
device_ids = [0,1]
pipe.unet.unetwrap = torch_neuronx.DataParallel(torch.jit.load(unet_filename), device_ids, set_dynamic_batching=False)

# Load other compiled models onto a single neuron core.
pipe.text_encoder = NeuronTextEncoder(pipe.text_encoder)
pipe.text_encoder.neuron_text_encoder = torch.jit.load(text_encoder_filename)

class NeuronTypeConversionWrapper(nn.Module):
    def __init__(self, post_quant_conv):
        super().__init__()
        self.network = post_quant_conv

    def forward(self, x):
        return self.network(x.float())
        
pipe.vae.decoder = NeuronTypeConversionWrapper(torch.jit.load(decoder_filename))
pipe.vae.post_quant_conv = NeuronTypeConversionWrapper(torch.jit.load(post_quant_conv_filename))

# Run pipeline
##prompt = ["a photo of an astronaut riding a horse on mars",
#          "sonic on the moon",
#          "elvis playing guitar while eating a hotdog",
#          "saved by the bell",
#          "engineers eating lunch at the opera",
#          "panda eating bamboo on a plane",
#          "A digital illustration of a steampunk flying machine in the sky with cogs and mechanisms, 4k, detailed, trending in artstation, fantasy vivid colors",
#          "kids playing soccer at the FIFA World Cup"
#         ]

# First do a warmup run so all the asynchronous loads can finish
#image_warmup = pipe(prompt[0]).images[0]

#plt.title("Image")
#plt.xlabel("X pixel scaling")
#plt.ylabel("Y pixels scaling")

#total_time = 0
#for x in prompt:
#    start_time = time.time()
#    image = pipe(x).images[0]
#    total_time = total_time + (time.time()-start_time)
#    r1 = random.randint(0,99999)
#    imgname="image"+str(r1)+".png"
#    image.save(imgname)
#    image = mpimg.imread(imgname)
#    clear_output(wait=True)
#    plt.imshow(image)
#    plt.show()
#print("Average time: ", np.round((total_time/len(prompt)), 2), "seconds")

def text2img(PROMPT):
    start_time = time.time()
    image = pipe(PROMPT).images[0]
    #image = pipe(x).images[0]
    total_time =  time.time()-start_time
    r1 = random.randint(0,99999)
    imgname="image"+str(r1)+".png"
    image.save(imgname)
    image = mpimg.imread(imgname)
    return image, str(total_time)

#app = gr.Interface(fn=text2img,
#    inputs=["text"],
#    outputs = [gr.Image(height=512, width=512), "text"],
#    title = 'Stable Diffusion 2.1 in AWS EC2 Inf2 instance')
#app.queue()
#app.launch(share = True,server_name="0.0.0.0",debug = False)

def prompt_paint(input_image, source_prompt, result_prompt):
  processor = CLIPSegProcessor.from_pretrained("CIDAS/clipseg-rd64-refined")
  model = CLIPSegForImageSegmentation.from_pretrained("CIDAS/clipseg-rd64-refined")
  prompts = source_prompt.split(sep=',')
  inputs = processor(text=prompts, images=[input_image] * len(prompts), padding="max_length", return_tensors="pt")
  with torch.no_grad():
    outputs = model(**inputs)
  #DEBUG need to check
  input_image.convert('RGB').resize((512, 512)).save("/init_image.png", "PNG")
  #DEBUG need to check
  preds = outputs.logits.unsqueeze(0)
  filename = f"/mask.png"
  plt.imsave(filename,torch.sigmoid(preds[0][0]))
  maskimage=Image.open(filename)
  print(f'source_prompt={source_prompt};type(source_prompt)={type(source_prompt)};prompts={prompts};type(prompts)={type(prompts)}',flush=True)
  image = pipe(prompt=result_prompt,image=input_image,mask_image=maskimage).images[0]
  return image

with gr.Blocks() as app:
  gr.Markdown("# stable-diffusion-2-inpainting")
  with gr.Tab("Prompt basic"):
    with gr.Row():
      input_image = gr.Image(label = 'Upload your input image', type = 'pil')
      source_prompt = gr.Textbox(label="What is in the input image you want to change? PLEASE add comma at the end")
      result_prompt = gr.Textbox(label="Replace it with?")
      image_output = gr.Image()
    image_button = gr.Button("Generate")
    image_button.click(prompt_paint, inputs=[input_image, source_prompt, result_prompt], outputs=image_output)

app.launch(share = True,server_name="0.0.0.0",debug = True)
