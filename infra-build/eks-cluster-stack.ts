import * as cdk from 'aws-cdk-lib';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import { GlobalResources } from "@aws-quickstart/eks-blueprints";
import { VpcResourceProvider } from "./vpc-resource-provider";
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as eks from "aws-cdk-lib/aws-eks";
import * as iam from "aws-cdk-lib/aws-iam";
import {UpdatePolicy} from "aws-cdk-lib/aws-autoscaling";
import {SubnetFilter,SubnetType,InstanceType} from "aws-cdk-lib/aws-ec2";
import {CapacityType,KubernetesVersion,MachineImageType} from 'aws-cdk-lib/aws-eks';
import {AccountRootPrincipal} from "aws-cdk-lib/aws-iam";

const version = 'auto';
let cluster_name = process.env.CLUSTER as string;

export class EksClusterStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const account = this.account;
    const region = this.region;

    const clusterVPC = new VpcResourceProvider();

    const addOns: Array<blueprints.ClusterAddOn> = [
      new blueprints.addons.MetricsServerAddOn(),
      new blueprints.addons.AwsLoadBalancerControllerAddOn(),
      new blueprints.addons.VpcCniAddOn(),
      new blueprints.addons.CoreDnsAddOn(),
      new blueprints.addons.KubeProxyAddOn(),
      new blueprints.addons.GpuOperatorAddon()
    ];

    const nodesProvider = new blueprints.GenericClusterProvider(
        {
          clusterName: `${cluster_name}`,
          mastersRole: blueprints.getResource(context => {
                    return new iam.Role(context.scope, 'AdminRole', { assumedBy: new AccountRootPrincipal() });
          }),
          vpcSubnets: [{ availabilityZones: ['us-west-2a','us-west-2b','us-west-2c','us-west-2d'] }],
          autoscalingNodeGroups: [
            {
              id: "core",
              autoScalingGroupName: "core",
              allowAllOutbound: true,
              minSize: 1,
              maxSize: 3,
              machineImageType: MachineImageType.AMAZON_LINUX_2,
              nodeGroupSubnets: {subnetType: SubnetType.PUBLIC ,subnetFilters: [SubnetFilter.availabilityZones(['us-west-2a', 'us-west-2b', 'us-west-2c', 'us-west-2d'])]},
            },
            {
              id: "edge",
              autoScalingGroupName: "edge",
              minSize: 1,
              maxSize: 3,
              machineImageType: MachineImageType.AMAZON_LINUX_2,
              nodeGroupSubnets: {subnetType: SubnetType.PUBLIC ,subnetFilters: [SubnetFilter.availabilityZones(['us-west-2a', 'us-west-2b', 'us-west-2c', 'us-west-2d'])]},
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
        .addOns(...addOns)
        .teams()
        .useDefaultSecretEncryption(false) //false to turn secret encryption off (demo cases)
        .build(this, cluster_name);
  }
}
