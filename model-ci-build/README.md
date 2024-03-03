
* Fork https://github.com/aws-samples/edge_diffusion_on_eks/ and populate the `GITHUB_USER`.
* Check the latest [DLC](https://github.com/aws/deep-learning-containers/blob/master/available_images.md) for `BASE_IMAGE_AMD_XLA_TAG` and `BASE_IMAGE_AMD_CUD_TAG` values.
* Export the following variables
```bash
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --output text --query Account)
export AWS_REGION=us-west-2
export BASE_IMAGE_AMD_XLA_TAG=1.13.1-neuronx-py310-sdk2.17.0-ubuntu20.04 
export BASE_IMAGE_AMD_CUD_TAG=2.0.1-gpu-py310-cu118-ubuntu20.04-ec2
export BASE_IMAGE_ARM_CUD_TAG=pytorch-inference-graviton-2.1.0-cpu-py310-ubuntu20.04-ec2
export IMAGE_AMD_XLA_TAG=amd64-neuron
export IMAGE_AMD_CUD_TAG=amd64-cuda
export IMAGE_ARM_CUD_TAG=arm64-cuda
export BASE_REPO=stablediffusion
export BASE_TAG=multiarch-ubuntu
export BASE_ARM_TAG=arm64
export BASE_AMD_TAG=amd64
export GITHUB_BRANCH=master
export GITHUB_USER=yahavb
export GITHUB_REPO=edge_diffusion_on_eks
export MODEL_DIR=sd2_compile_dir
```

```bash
cd ci-build
./deploy-pipeline.sh
```
