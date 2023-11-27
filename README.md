# edge_diffusion inferences
Images, audio, and video content in augmented reality (AR) applications must be generated within milliseconds. Therefore, AR applications generate digital content on-device, but quality is limited by device capabilities. However, content created on a remote server with enough resources takes sub-seconds to be served. As on-device models enrich, this trend pushes inference capabilities back to the cloud within the submillisecond timeframe that cloud edge services such as CDN and LocalZone offer.

This sample illustrates how AWS helps host models like Stable Diffusion by Stability AI on any available AI chip like NVIDIA or Neuron-based AI accelerators as close as possible to the user device enabling the AR app developer to decouple the user device hardware from content quality.  

We compiled and deployed Stable Diffusion 2.1 on EKS in LocalZone to 1/ reduce deploy-time by caching 20GB model's graph artifacts on LocalZone with Docker multi-stage. 2/ simplify a secured network path between the user device and remote server with K8s node-port service; and finally 3/ run the model on any compatible and available AI accelerators. 

## Setup
* [Create EKS cluster and deploy Karpenter](https://karpenter.sh/docs/getting-started/getting-started-with-karpenter/) 
* Use Service Quotas console to allocate Amazon Elastic Compute Cloud (Amazon EC2) "Running On-Demand Inf instances" and "Running On-Demand G and VT instances" limits.
* Configure NodePools to set Inferentia2 and G EC2 instances constraints 
  ```bash
  kubectl apply -f amd-neuron-provisioner.yaml
  ```
* Deploy the [Volcano CRD](https://volcano.sh/en/docs/installation/)
* Deploy [Container Insights on Amazon EKS](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Container-Insights-setup-EKS-quickstart.html)
* Deploy [NVIDIA device plugin for Kubernetes](https://github.com/NVIDIA/k8s-device-plugin)
  ```bash
  kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.1/nvidia-device-plugin.yml
  ```
* Deploy [Neuron device plugin for Kubernetes](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/containers/tutorials/k8s-setup.html#tutorial-k8s-env-setup-for-neuron)
  ```bash
  kubectl apply -f k8s-neuron-device-plugin-rbac.yml
  kubectl apply -f k8s-neuron-device-plugin-ds.yml
  ```

## Build multi-arch CPU and accelerator image
The build process creates OCI images for x86-based instances. You add another build step to create OCI images for Graviton-based instances. This new build process creates a OCI image manifest list that references both OCI images. The container runtime (Docker Engine or containerd) will pull the correct platform-specific image at deployment time. To automate the OCI image build process, we use AWS CodePipeline. AWS CodePipeline starts by building a OCI image from the code in AWS CodeBuild that is pushed to Amazon Elastic Container Registry (Amazon ECR). 

* [Deploy the CI-pipeline of the Stable Diffusion image](./ci-build)

* Deploy node pools on LocalZone
TBD
