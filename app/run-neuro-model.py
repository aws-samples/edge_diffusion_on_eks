# --- Load all compiled models ---
COMPILER_WORKDIR_ROOT = 'sd_1_5_fp32_512_compile_workdir'

# Model ID for SD version pipeline
model_id = "runwayml/stable-diffusion-v1-5"

pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)

text_encoder_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'text_encoder/model.pt')
unet_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'unet/model.pt')
decoder_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'vae_decoder/model.pt')
post_quant_conv_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'vae_post_quant_conv/model.pt')
safety_model_neuron_filename = os.path.join(COMPILER_WORKDIR_ROOT, 'safety_model_neuron/model.pt')


# Load the compiled UNet onto two neuron cores.
pipe.unet = NeuronUNet(UNetWrap(pipe.unet))
device_ids = [0,1]
pipe.unet.unetwrap = torch_neuronx.DataParallel(torch.jit.load(unet_filename), device_ids, set_dynamic_batching=False)

# Load other compiled models onto a single neuron core.
pipe.text_encoder = NeuronTextEncoder(pipe.text_encoder)
pipe.text_encoder.neuron_text_encoder = torch.jit.load(text_encoder_filename)
pipe.vae.decoder = torch.jit.load(decoder_filename)
pipe.vae.post_quant_conv = torch.jit.load(post_quant_conv_filename)
pipe.safety_checker.vision_model = NeuronSafetyModelWrap(torch.jit.load(safety_model_neuron_filename))

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

plt.title("Image")
plt.xlabel("X pixel scaling")
plt.ylabel("Y pixels scaling")

total_time = 0
for x in prompt:
    start_time = time.time()
    image = pipe(x).images[0]
    total_time = total_time + (time.time()-start_time)
    image.save("image.png")
    image = mpimg.imread("image.png")
    #clear_output(wait=True)
    plt.imshow(image)
    plt.show()
print("Average time: ", np.round((total_time/len(prompt)), 2), "seconds")
