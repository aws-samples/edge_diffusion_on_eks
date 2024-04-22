import os
os.environ["NEURON_FUSE_SOFTMAX"] = "1"
model_id=os.environ['MODEL_ID']
device=os.environ["DEVICE"]
model_dir=os.environ['COMPILER_WORKDIR_ROOT']
height=os.environ['HEIGHT']
width=os.environ['WIDTH']
from optimum.neuron import NeuronStableDiffusionPipeline

compiler_args = {"auto_cast": "matmul", "auto_cast_type": "bf16"}
input_shapes = {"batch_size": 1, "height": height, "width": width}
stable_diffusion = NeuronStableDiffusionPipeline.from_pretrained(model_id, export=True, **compiler_args, **input_shapes)
stable_diffusion.save_pretrained(model_dir)

