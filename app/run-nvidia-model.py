print("import",flush=True)
import random
import os

import torch
import torch.nn as nn
import numpy as np

from matplotlib import pyplot as plt
from matplotlib import image as mpimg
import time
import copy
from IPython.display import clear_output
from PIL import Image

import requests

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
COMPILER_WORKDIR_ROOT = 'sd2_compile_dir_512'
model_id = "stabilityai/stable-diffusion-2-inpainting"
text_encoder_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'text_encoder/model.pt')
decoder_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'vae_decoder/model.pt')
unet_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'unet/model.pt')
post_quant_conv_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'vae_post_quant_conv/model.pt')

#pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=DTYPE)
pipe = DiffusionPipeline.from_pretrained(model_id, torch_dtype=DTYPE)
pipe = pipe.to("cuda")
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

# Replaces StableDiffusionPipeline's decode_latents method with our custom decode_latents method defined above.
#StableDiffusionPipeline.decode_latents = decode_latents
DiffusionPipeline.decode_latents = decode_latents

# Run pipeline
prompt = ["a photo of an astronaut riding a horse on mars",
          "sonic on the moon",
          "elvis playing guitar while eating a hotdog",
          "saved by the bell",
          "engineers eating lunch at the opera",
          "panda eating bamboo on a plane",
          "A digital illustration of a steampunk flying machine in the sky with cogs and mechanisms, 4k, detailed, trending in artstation, fantasy vivid colors",
          "kids playing soccer at the FIFA World Cup"
         ]

# First do a warmup run so all the asynchronous loads can finish
#initimage = Image.open('/init_image.png')
#maskimage=Image.open('/mask_image.png')
#image = pipe(prompt=prompt[0],image=initimage,mask_image=maskimage).images[0]

#total_time = 0
#for x in prompt:
#    start_time = time.time()
#    image = pipe(prompt=x,image=initimage,mask_image=maskimage).images[0]
#    total_time = total_time + (time.time()-start_time)
#    r1 = random.randint(0,99999)
#    imgname="image"+str(r1)+".png"
#    image.save(imgname)
#    image = mpimg.imread(imgname)
#    clear_output(wait=True)
    #plt.imshow(image)
    #plt.show()
#print("Average time: ", np.round((total_time/len(prompt)), 2), "seconds")

def text2img(PROMPT):
  start_time = time.time()
  image = pipe(PROMPT).images[0]
  total_time =  time.time()-start_time
  r1 = random.randint(0,99999)
  imgname="image"+str(r1)+".png"
  image.save(imgname)
  image = mpimg.imread(imgname)
  return image, str(total_time)

def prompt_paint(input_image, source_prompt, result_prompt):
  url = "https://github.com/timojl/clipseg/blob/master/example_image.jpg?raw=true"
  manual_image = Image.open(requests.get(url, stream=True).raw)
  print(f'type(manual_image)={manual_image};type(input_image)={type(input_image)}; source_prompt={source_prompt}; result_prompt={result_prompt}',flush=True)
  processor = CLIPSegProcessor.from_pretrained("CIDAS/clipseg-rd64-refined")
  model = CLIPSegForImageSegmentation.from_pretrained("CIDAS/clipseg-rd64-refined") 
  inputs = processor(text=source_prompt, images=[manual_image] * len(source_prompt), padding="max_length", return_tensors="pt")
  with torch.no_grad():
    outputs = model(**inputs)
  preds = outputs.logits.unsqueeze(1)
  filename = f"/mask.png"
  plt.imsave(filename,torch.sigmoid(preds[0][0]))
  maskimage=PIL.Image.open(filename)
  image = pipe(prompt=result_prompt,image=input_image,mask_image=maskimage).images[0]
  return image

with gr.Blocks() as app:
  gr.Markdown("# stable-diffusion-2-inpainting")
  with gr.Tab("Prompt basic"):
    with gr.Row():
      input_image = gr.Image(label = 'Upload your input image', type = 'pil')
      source_prompt = gr.Textbox(label="What is in the input image you want to change?")
      result_prompt = gr.Textbox(label="Replace it with?")
      image_output = gr.Image()
    image_button = gr.Button("Generate")
    image_button.click(prompt_paint, inputs=[input_image, source_prompt, result_prompt], outputs=image_output)
  
app.launch(share = True,server_name="0.0.0.0",debug = True)

#app = gr.Interface(fn=text2img,
#    inputs=["text"],
#    outputs = [gr.Image(height=512, width=512), "text"],
#    title = 'Stable Diffusion 2 Inpainting 2.1 on AWS EC2 G5 instance')
#app.queue()
#app.launch(share = True,server_name="0.0.0.0",debug = False)
