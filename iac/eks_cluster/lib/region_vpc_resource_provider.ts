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
        return new ec2.Vpc(context.scope, 'eks-edge-vpc3', {
            ipAddresses: ec2.IpAddresses.cidr('10.0.0.0/16'),
            natGateways: 0,
            //availabilityZones: ['us-west-2a','us-west-2b','us-west-2-lax-1a','us-west-2-lax-1b'], // VPC spans all AZs
            subnetConfiguration: [ {
                cidrMask: 26,
                name: 'public-eks-subnet',
                subnetType: SubnetType.PUBLIC,
                //mapPublicIpOnLaunch: true
            },
                {
                    cidrMask: 26,
                    name: 'private-eks-subnet',
                    subnetType: SubnetType.PRIVATE_WITH_EGRESS
                },

            ]
        });
    }
}