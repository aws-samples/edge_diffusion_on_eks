import {Stack,StackProps, App} from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import {ResourceContext, ResourceProvider} from "@aws-quickstart/eks-blueprints";
import {IVpc, SubnetType} from "aws-cdk-lib/aws-ec2";

export class VpcResourceProvider implements ResourceProvider<IVpc> {
    provide(context: ResourceContext): IVpc {
        return new ec2.Vpc(context.scope, 'vpc', {
            ipAddresses: ec2.IpAddresses.cidr('10.0.0.0/16'),
            natGateways: 0,
            availabilityZones: ['us-west-2a','us-west-2b','us-west-2c','us-west-2d'],
            //availabilityZones: ['us-west-2d','us-west-2b'], 
            subnetConfiguration: [ 
              {
                cidrMask: 26,
                name: 'public',
                subnetType: SubnetType.PUBLIC,
                mapPublicIpOnLaunch: true
              },
              {
                cidrMask: 26,
                name: 'private',
                subnetType: SubnetType.PRIVATE_WITH_EGRESS
              },
            ]
        });
    }
}
