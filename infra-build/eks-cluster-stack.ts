import * as cdk from 'aws-cdk-lib';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import { GlobalResources } from "@aws-quickstart/eks-blueprints";
import { VpcResourceProvider } from "./vpc-resource-provider";
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as eks from "aws-cdk-lib/aws-eks";
import {UpdatePolicy} from "aws-cdk-lib/aws-autoscaling";
import {SubnetType,InstanceType} from "aws-cdk-lib/aws-ec2";
import {CapacityType,KubernetesVersion,MachineImageType} from 'aws-cdk-lib/aws-eks';

const version = 'auto';
let cluster_name = process.env.CLUSTER as string;

export class EksClusterStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const account = this.account;
    const region = this.region;

    const clusterVPC = new VpcResourceProvider();

    /*const addOns: Array<blueprints.ClusterAddOn> = [
      new blueprints.addons.MetricsServerAddOn(),
      new blueprints.addons.ClusterAutoScalerAddOn(),
      new blueprints.addons.AwsLoadBalancerControllerAddOn(),
      new blueprints.addons.VpcCniAddOn(),
      new blueprints.addons.CoreDnsAddOn(),
      new blueprints.addons.KubeProxyAddOn()
    ];*/

    const nodesProvider = new blueprints.GenericClusterProvider(
        {
          clusterName: `${cluster_name}`,
          autoscalingNodeGroups: [
            {
              id: "core",
              autoScalingGroupName: "core",
              minSize: 1,
              maxSize: 3,
              machineImageType: MachineImageType.AMAZON_LINUX_2
            },
            {
              id: "edge",
              autoScalingGroupName: "edge",
              minSize: 1,
              maxSize: 3,
              machineImageType: MachineImageType.AMAZON_LINUX_2,
              //instanceType: new ec2.InstanceType('g5.4xlarge'),
              //nodeGroupSubnets: {availabilityZones: ['us-west-2-lax-1a']},
            }
          ]
        }
    )

    const stack = blueprints.EksBlueprint.builder()
        .resourceProvider(GlobalResources.Vpc, clusterVPC)
        .clusterProvider(nodesProvider)
        .account(account)
        .region(region)
        .version(version)
        //.addOns(...addOns)
        .useDefaultSecretEncryption(false) //false to turn secret encryption off (demo cases)
        .build(this, cluster_name);
  }
}
