import * as cdk from 'aws-cdk-lib';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import {GlobalResources } from "@aws-quickstart/eks-blueprints";
import {VpcResourceProvider } from "./vpc-resource-provider";
import {EndpointAccess,MachineImageType} from 'aws-cdk-lib/aws-eks';
import {SubnetFilter,SubnetType} from "aws-cdk-lib/aws-ec2";
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
      new blueprints.addons.GpuOperatorAddon()
    ];

    const nodesProvider = new blueprints.GenericClusterProvider(
        {
          clusterName: `${cluster_name}`,
          vpcSubnets: [{ availabilityZones: ['us-west-2a','us-west-2b','us-west-2c','us-west-2d'] }],
          endpointAccess: EndpointAccess.PUBLIC,
          autoscalingNodeGroups: [
            {
              id: "core",
              autoScalingGroupName: "core",
              allowAllOutbound: true,
              desiredSize: 3,
              minSize: 1,
              maxSize: 3,
              machineImageType: MachineImageType.AMAZON_LINUX_2,
              nodeGroupSubnets: {subnetType: SubnetType.PUBLIC ,subnetFilters: [SubnetFilter.availabilityZones(['us-west-2a', 'us-west-2b', 'us-west-2c', 'us-west-2d'])]},
            },
            {
              id: "edge",
              autoScalingGroupName: "edge",
              allowAllOutbound: true,
              desiredSize: 3,
              minSize: 1,
              maxSize: 3,
              machineImageType: MachineImageType.AMAZON_LINUX_2,
              nodeGroupSubnets: {subnetType: SubnetType.PUBLIC ,subnetFilters: [SubnetFilter.availabilityZones(['us-west-2-lax-1a'])]},
            },
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
