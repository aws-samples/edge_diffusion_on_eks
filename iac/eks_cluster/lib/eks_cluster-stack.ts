import * as cdk from 'aws-cdk-lib';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import { GlobalResources } from "@aws-quickstart/eks-blueprints";
import { VpcResourceProvider } from "./vpc_resource_provider";



const version = 'auto';
const cluster_name = 'eks-edge-cluster';

export class EksClusterStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const account = this.account;
    const region = this.region;




    const addOns: Array<blueprints.ClusterAddOn> = [
      new blueprints.addons.MetricsServerAddOn(),
      new blueprints.addons.ClusterAutoScalerAddOn(),
      new blueprints.addons.AwsLoadBalancerControllerAddOn(),
      new blueprints.addons.VpcCniAddOn(),
      new blueprints.addons.CoreDnsAddOn(),
      new blueprints.addons.KubeProxyAddOn()
    ];

    const stack = blueprints.EksBlueprint.builder()
        .resourceProvider(GlobalResources.Vpc, new VpcResourceProvider())
        .account(account)
        .region(region)
        .version(version)
        .addOns(...addOns)
        .useDefaultSecretEncryption(false) // set to false to turn secret encryption off (non-production/demo cases)
        .build(this, cluster_name);
  }
}