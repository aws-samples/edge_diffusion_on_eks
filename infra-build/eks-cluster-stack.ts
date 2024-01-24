import * as cdk from 'aws-cdk-lib';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import {GlobalResources} from '@aws-quickstart/eks-blueprints';
import {VpcResourceProvider} from './region_vpc_resource_provider';
import {EndpointAccess, MachineImageType} from 'aws-cdk-lib/aws-eks';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import {SubnetFilter, SubnetType} from 'aws-cdk-lib/aws-ec2';


const version = "auto";
const cluster_name = 'edge-eks-cluster';


export class EksClusterStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const account = this.account;
    const region = this.region;


    const regionVPC = new VpcResourceProvider();

    const karpenterAddOnProps = {
      requirements: [
        { key: 'node.kubernetes.io/instance-type', op: 'In', vals: ['g4dn.2xlarge'] },
        { key: 'topology.kubernetes.io/zone', op: 'In', vals: ['us-west-2-lax-1a', 'us-west-2-lax-1b']},
        { key: 'kubernetes.io/arch', op: 'In', vals: ['amd64']},
        { key: 'karpenter.sh/capacity-type', op: 'In', vals: ['on-demand']},
      ],
      subnetTags: {
        "aws-cdk:subnet-type": "Public",

      },
      securityGroupTags: {
        "Name": "EksClusterStack/edge-eks-cluster/edge-eks-cluster/inference",
      },
      taints: [{
        key: "core-node",
        value: "true",
        effect: "NoSchedule",
      }],
      amiFamily: "AL2",
      amiSelector: {
        'karpenter.sh/discovery/eks-edge-cluster': '*',
      },
      consolidation: { enabled: true },
      ttlSecondsUntilExpired: 2592000,
      weight: 20,
      interruptionHandling: true,
      tags: {
        schedule: 'always-on'
      },
      blockDeviceMappings: [{
        deviceName: "/dev/xvda",
        ebs: {
          volumeSize: 100,
          volumeType: ec2.EbsDeviceVolumeType.GP3,
          deleteOnTermination: true
        },
      }],
    };

    const addOns: Array<blueprints.ClusterAddOn> = [
      new blueprints.addons.MetricsServerAddOn(),
      new blueprints.addons.AwsLoadBalancerControllerAddOn(),
      new blueprints.addons.VpcCniAddOn(),
      new blueprints.addons.CoreDnsAddOn(),
      new blueprints.addons.GpuOperatorAddon(),
      new blueprints.addons.KarpenterAddOn({

      })

    ];

    const nodesProvider = new blueprints.GenericClusterProvider(
        {
          clusterName: cluster_name,
          vpcSubnets: [{availabilityZones: ['us-west-2a', 'us-west-2b', 'us-west-2c', 'us-west-2d']}],
          endpointAccess: EndpointAccess.PUBLIC,
          autoscalingNodeGroups: [
            {
              id: "core",
              autoScalingGroupName: "core-nodes-asg",
              desiredSize: 3,
              minSize: 1,
              maxSize: 3,
              allowAllOutbound: true,
              machineImageType: MachineImageType.AMAZON_LINUX_2,
              nodeGroupSubnets: {subnetType: SubnetType.PUBLIC ,subnetFilters: [SubnetFilter.availabilityZones(['us-west-2a', 'us-west-2b', 'us-west-2c', 'us-west-2d'])]},
            },
            {
              id: "inference",
              autoScalingGroupName: "inference-nodes-asg",
              instanceType: new ec2.InstanceType('g4dn.2xlarge'),
              allowAllOutbound: true,
              associatePublicIpAddress: true,
              desiredSize: 3,
              minSize: 1,
              maxSize: 3,
              machineImageType: MachineImageType.AMAZON_LINUX_2,
              nodeGroupSubnets: { subnetType: SubnetType.PUBLIC,subnetFilters: [SubnetFilter.availabilityZones(['us-west-2-lax-1a', 'us-west-2-lax-1b'])]},

            }
          ]
        }
    );

    const stack = blueprints.EksBlueprint.builder()
        .resourceProvider(GlobalResources.Vpc, regionVPC)
        .clusterProvider(nodesProvider)
        .account(account)
        .region(region)
        .version(version)
        .teams()
        .addOns(...addOns)
        .useDefaultSecretEncryption(false) // set to false to turn secret encryption off (non-production/demo cases)
        .build(this, cluster_name);

  }
}
