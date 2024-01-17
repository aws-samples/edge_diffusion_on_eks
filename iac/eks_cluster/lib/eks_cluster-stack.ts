import * as cdk from 'aws-cdk-lib';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import {GlobalResources} from '@aws-quickstart/eks-blueprints';
import {VpcResourceProvider} from './region_vpc_resource_provider';
import {CapacityType, KubernetesVersion, MachineImageType} from 'aws-cdk-lib/aws-eks';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import {SubnetType} from "aws-cdk-lib/aws-ec2";

const version = 'auto';
const cluster_name = 'edge-inference-cluster3';

export class EksClusterStack extends cdk.Stack {
    constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        const account = this.account;
        const region = this.region;

        //const edgeVPC = new VpcResourceProvider();
        const regionVPC = new VpcResourceProvider();

        const addOns: Array<blueprints.ClusterAddOn> = [
            new blueprints.addons.MetricsServerAddOn(),
            new blueprints.addons.ClusterAutoScalerAddOn(),
            new blueprints.addons.AwsLoadBalancerControllerAddOn(),
            new blueprints.addons.VpcCniAddOn(),
            new blueprints.addons.CoreDnsAddOn(),
            new blueprints.addons.KubeProxyAddOn()
        ];



        /*const coreNodesProvider = new blueprints.MngClusterProvider(
            {
                 id: "core",
                 version: KubernetesVersion.of("auto"),
                 desiredSize: 3,
                 nodeGroupCapacityType: CapacityType.ON_DEMAND,
                 minSize: 1,
                 maxSize: 3,
                 nodeGroupSubnets: { availabilityZones: ['us-west-2a', 'us-west-2b'] },
                 clusterName: `${cluster_name}`
             }
         )*/

        const edgeNodesProvider = new blueprints.AsgClusterProvider(
            {
                id: "inference",
                //vpc: edgeVPC.provide().vpcId,
                version: KubernetesVersion.of("auto"),
                desiredSize: 3,
                minSize: 1,
                maxSize: 3,
                machineImageType: MachineImageType.AMAZON_LINUX_2,
                instanceType: new ec2.InstanceType('g5.4xlarge'),
                //nodeGroupSubnets: { availabilityZones: ['us-west-2-lax-1a','us-west-2-lax-1b'] },
                autoScalingGroupName: "edge-nodes-asg",
                clusterName: `${cluster_name}`,
                vpcSubnets: [ {subnetType:SubnetType.PUBLIC }],

            }
        );

        const stack = blueprints.EksBlueprint.builder()
            .resourceProvider(GlobalResources.Vpc, regionVPC)
            //.clusterProvider(coreNodesProvider)
            .clusterProvider(edgeNodesProvider)
            .account(account)
            .region(region)
            .version(version)
            .addOns(...addOns)
            .useDefaultSecretEncryption(false) // set to false to turn secret encryption off (non-production/demo cases)
            .build(this, cluster_name);

    }
}
