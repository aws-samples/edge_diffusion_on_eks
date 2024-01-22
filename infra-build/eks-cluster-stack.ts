import * as cdk from 'aws-cdk-lib';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import {GlobalResources} from '@aws-quickstart/eks-blueprints';
import {VpcResourceProvider} from './region_vpc_resource_provider';
import {EndpointAccess, MachineImageType} from 'aws-cdk-lib/aws-eks';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from "aws-cdk-lib/aws-iam";
import {SubnetType} from "aws-cdk-lib/aws-ec2";


const version = "auto";
const cluster_name = 'edge-eks-cluster';


export class EksClusterStack extends cdk.Stack {
    constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        const account = this.account;
        const region = this.region;


        const regionVPC = new VpcResourceProvider();

        const addOns: Array<blueprints.ClusterAddOn> = [
            new blueprints.addons.MetricsServerAddOn(),
            new blueprints.addons.AwsLoadBalancerControllerAddOn(),
            new blueprints.addons.VpcCniAddOn(),
            new blueprints.addons.CoreDnsAddOn()
        ];

        const nodesProvider = new blueprints.GenericClusterProvider(
            {
                clusterName: cluster_name,
                vpcSubnets: [{availabilityZones: ['us-west-2a', 'us-west-2b', 'us-west-2c', 'us-west-2d']}],
                endpointAccess: EndpointAccess.PUBLIC,
                //placeClusterHandlerInVpc: true,
                autoscalingNodeGroups: [
                    {
                        id: "core",
                        autoScalingGroupName: "core-nodes-asg",
                        desiredSize: 3,
                        minSize: 1,
                        maxSize: 3,
                        machineImageType: MachineImageType.AMAZON_LINUX_2,
                        nodeGroupSubnets: {availabilityZones: ['us-west-2a', 'us-west-2b', 'us-west-2c', 'us-west-2d']}
                    },
                    {
                        id: "inference",
                        autoScalingGroupName: "inference-nodes-asg",
                        instanceType: new ec2.InstanceType('g4dn.2xlarge'),
                        desiredSize: 3,
                        minSize: 1,
                        maxSize: 3,
                        machineImageType: MachineImageType.AMAZON_LINUX_2,
                        nodeGroupSubnets: {availabilityZones: ['us-west-2-lax-1a', 'us-west-2-lax-1b']}

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
