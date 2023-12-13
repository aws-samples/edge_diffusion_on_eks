import {Stack,StackProps, App} from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import {ResourceContext, ResourceProvider} from "@aws-quickstart/eks-blueprints";
import {IVpc, SubnetType} from "aws-cdk-lib/aws-ec2";


/*const PARENT_REGION_AZ = 'us-west-2';
const LOCAL_ZONE_AZ = 'us-west-2-lax-1a';

const VPC_CIDR = '10.0.0.0/16';
const SUBNET_SIZE = 26;*/


export class VpcResourceProvider implements ResourceProvider<IVpc> {
    provide(context: ResourceContext): IVpc {
        return new ec2.Vpc(context.scope, 'eks-edge-vpc', {
            ipAddresses: ec2.IpAddresses.cidr('10.0.0.0/16'),
            availabilityZones: ['us-west-2-lax-1a', 'us-west-2a'], // VPC spans all AZs
            subnetConfiguration: [ {
                cidrMask: 26,
                name: 'public-eks-subnet',
                subnetType: SubnetType.PUBLIC,
                mapPublicIpOnLaunch: true
            },
                {
                    cidrMask: 26,
                    name: 'private-eks-subnet',
                    subnetType: SubnetType.PRIVATE_WITH_EGRESS
                },

            ],
            natGatewaySubnets: {
                availabilityZones: ['us-west-2-lax-1a'], // NAT gateway only in 1 AZ
                subnetType: SubnetType.PUBLIC
            }
        });
    }
}


/*export class VPCStack extends Stack {
    public readonly vpc: ec2.Vpc;

    get availabilityZones() {
        return [
            PARENT_REGION_AZ,
            LOCAL_ZONE_AZ,
        ];
    }

    constructor(scope: App, id: string, props?: StackProps) {
        super(scope, id, props);

        this.vpc = new ec2.Vpc(this, 'edge-cluster-vpc', {
            ipAddresses: ec2.IpAddresses.cidr(VPC_CIDR),
            vpcName: 'edge-cluster-vpc',
            subnetConfiguration: [
                {
                    cidrMask: SUBNET_SIZE,
                    name: 'public-subnet-lz',
                    subnetType: ec2.SubnetType.PUBLIC,
                    availabilityZones: [LOCAL_ZONE_AZ],
                    mapPublicIpOnLaunch: true,

                },
                {
                    cidrMask: SUBNET_SIZE,
                    name: 'public-subnet-ir',
                    subnetType: ec2.SubnetType.PUBLIC,
                    availabilityZones: [PARENT_REGION_AZ],
                    mapPublicIpOnLaunch: true
                }
            ]

        });

        this.vpc.publicSubnet.addTags({
            'kubernetes.io/cluster/eks-edge-cluster': 'shared',
            'kubernetes.io/role/elb': '1'
        });




    }
}*/
