import * as cdk from 'aws-cdk-lib';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import { GlobalResources } from "@aws-quickstart/eks-blueprints";
import { VpcResourceProvider } from "./vpc-resource-provider";

import * as eks from "aws-cdk-lib/aws-eks";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import {UpdatePolicy} from "aws-cdk-lib/aws-autoscaling";
import {SubnetType,InstanceType} from "aws-cdk-lib/aws-ec2";
import {CapacityType,KubernetesVersion,MachineImageType} from 'aws-cdk-lib/aws-eks';

const version = 'auto';
let cluster_name = process.env.CF_STACK as string;

export class EksClusterStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const account = this.account;
    const region = this.region;

    const regionVPC = new VpcResourceProvider();
    const edgeVPC = new VpcResourceProvider();

    const addOns: Array<blueprints.ClusterAddOn> = [
      new blueprints.addons.MetricsServerAddOn(),
      new blueprints.addons.ClusterAutoScalerAddOn(),
      new blueprints.addons.AwsLoadBalancerControllerAddOn(),
      new blueprints.addons.VpcCniAddOn(),
      new blueprints.addons.CoreDnsAddOn(),
      new blueprints.addons.KubeProxyAddOn()
    ];

    const coreClusterProvider = new blueprints.MngClusterProvider(
        {
          id: "core",
          version: KubernetesVersion.of("auto"),
          desiredSize: 3,
          minSize: 1,
          maxSize: 3,
          nodeGroupCapacityType: CapacityType.ON_DEMAND,
          clusterName: `${cluster_name}`,
          nodeGroupSubnets: { availabilityZones: ['us-west-2a','us-west-2b','us-west-2c'] },
        }
    )

    const edgeClusterProvider = new blueprints.MngClusterProvider(
        {
          id: "edge",
          autoScalingGroupName: "edge-nodes-asg",
          version: KubernetesVersion.of("auto"),
          desiredSize: 3,
          minSize: 1,
          maxSize: 3,
          nodeGroupCapacityType: CapacityType.ON_DEMAND,
          machineImageType: MachineImageType.AMAZON_LINUX_2,
          instanceType: new ec2.InstanceType('g5.4xlarge'),
          clusterName: `${cluster_name}`,
          vpcSubnets: [ {subnetType:SubnetType.PUBLIC }],
        }
    )


    const stack = blueprints.EksBlueprint.builder()
        .resourceProvider(GlobalResources.Vpc, clusterVPC)
        .clusterProvider(coreClusterProvider)
        .clusterProvider(edgeClusterProvider)
        .account(account)
        .region(region)
        .version(version)
        .addOns(...addOns)
        .useDefaultSecretEncryption(false) //false to turn secret encryption off (demo cases)
        .build(this, cluster_name);
  }
}
