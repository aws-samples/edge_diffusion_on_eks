
* Fork https://github.com/aws-samples/edge_diffusion_on_eks/ and populate the `GITHUB_USER`.
* Export the following variables
```bash
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --output text --query Account)
export AWS_REGION=us-west-2
export BASE_IMAGE_AMD_XLA_TAG=1.13.1-neuronx-py310-sdk2.14.1-ubuntu20.04
export BASE_IMAGE_AMD_CUD_TAG=2.0.1-gpu-py310-cu118-ubuntu20.04-ec2
export IMAGE_AMD_XLA_TAG=amd64-neuron
export IMAGE_AMD_CUD_TAG=amd64-cuda
export BASE_REPO=stablediffusion
export BASE_TAG=multiarch-ubuntu
export BASE_ARM_TAG=arm64
export BASE_AMD_TAG=amd64
export GITHUB_BRANCH=master
export GITHUB_USER=yahavb
export GITHUB_REPO=edge_diffusion_on_eks
```

```bash
cd ci-build
./deploy-pipeline.sh
```
