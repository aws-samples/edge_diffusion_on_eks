## Spotable Game Server

This is an example of a dedicated game-server deployment in EKS using Spot Amazon EC2 Instances. The goal is to provide a robust and straightforward game-server deployment pattern on EKS. 

We use Minecraft as the example deployed based on [minecraft helm chart](https://hub.docker.com/r/itzg/minecraft-server/) with a slight modification in the deployment mechanism.
Launching game-server in EKS can be done in several ways. The first is using k8s native constructs such as Deployment with customized wrappers, e.g., [start.py](https://github.com/aws-samples/spotable-game-server/blob/master/minecraft-server-image/start.py). Also, it can use [Init Containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/) that decouples the function that contains utilities or setup scripts not present in the game-server image. Finally, a dedicated game-server CRD that points k8s to use specific init containers per game-server type. We are going to cover the three cases herein. 


## License Summary

This sample code is made available under a modified MIT license. See the LICENSE file.

## Game Server Common Functions and Utilities 

### Dynamic Port Allocation
The proposal herein deploys a dedicated game server as a k8s pod with `hostnetwork:true` option. Each k8s node (EC2 Instance) deployed with a public hostname, and high port range is opened for client connectivity. Upon a game-server scheduling (pod scheduling), two high ports are allocated for the game server. The clients will connect the game-server using the public hostname and port assigned. [start.py](https://github.com/aws-samples/spotable-game-server/blob/master/minecraft-server-image/start.py) act the game-server wrapper script for the original build. It uses a lazy-approach to generate the required set of dynamic high ports and passes it game-server as an environment variable upon the game-server init phase.  Initially, `socket.AF_INET` socket is started and bound to port `0`. The OS will allocate a socket on a high port. We will capture the port and release the socket right before we the server starts. There is a chance for a raise condition when multiple game-server will attempt to start on the same instance. That will resolve automatically by a continuous `CrashLoopBackOff`.  

``` python
def get_rand_port():
# Attempting to get random port
  try:
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',0))
  except socket.error as msg:
    print 'bind failed. Error is '+str(msg[0])+' Msg '+msg[1]
    print 'socket bind complete '
    port=s.getsockname()[1]
    s.close()
  return port
```

The proposed spec uses a [Deployment](https://github.com/aws-samples/spotable-game-server/blob/master/specs/minecraft-gs-r1-12-deploy.yaml) k8s resource type that uses standard  `containers` environment variables defining the game-server init parameters. 

### Game Server Inventory Mgmt. 
We used SQS as a mechanism to mediate between the game-server and external system that maintain the game-server fleet transient state. Any such method can read the messages published on that queue and take action. To enable SQS access on EKS, simply update your worker nodes IAM role by adding an inline policy with the proper `region`, `account-id`, and `queuename` defined in [start.py](https://github.com/aws-samples/spotable-game-server/blob/master/minecraft-server-image/start.py).

``` yaml
{
  "Version": "2012-10-17",
  "Statement": [
  {
    "Effect": "Allow",
    "Action": [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ],
  "Resource": "arn:aws:sqs:region:account-id:queuename"
  }
  ]
}
```

The EKS Bootstrap.sh script is packaged into the EKS Optimized AMI that we are using, and only requires a single input: the EKS Cluster name. The bootstrap script supports setting any kubelet-extra-args at runtime. You will need to configure node-labels so that kubernetes knows what type of nodes we have provisioned. Set the lifecycle for the nodes as `ondemand` or `spot`. Check out The Setup Process below for more information as well as [Improvements for Amazon EKS Worker Node Provisioning](https://aws.amazon.com/blogs/opensource/improvements-eks-worker-node-provisioning/).

### Managing Spot Nodes
Although Spot Instance interruption is less unlikely event during a live game, its impact is perceived as a significant annoyance by players. The following section proposes strategies to avoid these negative player impact that will be applied in the referenced architecture. In the case of interruption we will drain the node and notify the game server by sending SIGTERM signal. Node drainage requires an “agent” to pull potential spot interruption from CloudWatch or Instance Metadata. We are going to use the Instance Metadata notification as the notification latency is shorter than CloudWatch. 
* The agent,[spot-sig-handler-ds](https://github.com/aws-samples/spotable-game-server/blob/master/specs/spot-sig-handler-ds.yaml) is deployed as daemon set that runs on every node and will pull termination status from the instance metadata endpoint. 
* When a termination notification arrived, the `kubectl drain node` will be executed and a SIGTERM notification will be sent to the game-server pod.
* The game server will keep running for the next 120 sec to allow the game to notify the player about the incoming termination. 
* No new game-server will be scheduled on that node to be terminated as it marked as schedulable.
* A notification to external system like Match-Making system, the SQS queue in our case, will be sent to update the current available game-server inventory.

#### Optimization Opportunity for Spot Interruption Handeling 
In the case of the incoming player actions are served by UDP and it is required to mask the interruption from the player, the game-server allocator (EKS in our case) will schedule more than one game-server as a target upstream servers behind a UDP load balancer that multicast any packet received to the set of game-servers. The failover will occur seamlessly once the scheduler terminates the game-server upon node termination. This option is valid as it doubles and more the compute needed for the game server. 

## The Setup Process
* Create an EKS cluster using the [Getting Started with Amazon EKS](https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html) guide. The guestbook step is recommended for sanity test but not crucial to this scenario. 
* If an AWS Spot Instances is being used, apply [Step 3: Launch and Configure Amazon EKS Worker Nodes](https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html) from the guide but with Spot ASG. 
* One can use MixedInstancesPolicy where we allow EKS to opportunistically allocate compatibale spot instances for cost optimization.
For that, one should use the cloud formation template with the following parameters:

In our case, the Minecraft gameserver or any other gameserver exposed to the player thru ephemeral port allocated by [start.py](https://github.com/aws-samples/spotable-game-server/blob/master/minecraft-server-image/start.py). Hence `ExistingNodeSecurityGroups` should be populated with the security group that allows the network access.  

check the status of the node pool create cloudformation be executing:

``` bash
until [[ `aws cloudformation describe-stacks --stack-name "minecraft-mix-us-west2" --query "Stacks[0].[StackStatus]" --output text` == "CREATE_COMPLETE" ]]; do  echo "The stack is NOT in a state of CREATE_COMPLETE at `date`";   sleep 30; done && echo "The Stack is built at `date` - Please proceed"
```

* Add the new Worker Node Role ARN to the ConfigMap by discovering the new node role ARN using IAM console and execute [whitelist-worker-nodes.yaml](https://github.com/aws-samples/spotable-game-server/blob/master/specs/whitelist-worker-nodes.yaml)
* Deploy the Spot signal handler as daemon set using (spot-sig-handler-ds.yaml)[https://github.com/yahavb/simple-game-server-eks/blob/master/specs/spot-sig-handler-ds.yaml]
* Based on the node lables configured in the worker nodes provisioning set the `nodeSelector` with the proper `lifecycle` and `title` values. In out case:
``` yaml
nodeSelector:
lifecycle: spot
title: minecraft
```

* Deploy the Mincraft k8s Deployment [minecraft-r1-12-deploy.yaml](https://github.com/aws-samples/spotable-game-server/blob/master/specs/minecraft-r1-12-deploy.yaml) and discover public ip and port to conncet your Minecraft client by reading the init messages published by the game-server in the SQS queue. e.g.,

![alt text](https://github.com/aws-samples/spotable-game-server/blob/master/pics/gs_init_msg.png)

* Download Minecraft client e.g., https://minecraft.net/en-us/download/alternative/ configure the game server and enjoy


![alt text](https://github.com/aws-samples/spotable-game-server/blob/master/pics/demo_game.png)

