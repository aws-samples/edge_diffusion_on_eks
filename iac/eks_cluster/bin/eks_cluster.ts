#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { EksClusterStack } from '../lib/eks_cluster-stack';

const app = new cdk.App();
new EksClusterStack(app, 'EksClusterStack', {

  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },

});