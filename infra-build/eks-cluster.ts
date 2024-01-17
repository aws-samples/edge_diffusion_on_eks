#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { EksClusterStack } from './eks-cluster-stack';

const app = new cdk.App();
let stack = process.env.CF_STACK as string;

new EksClusterStack(app,stack,{
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
});
