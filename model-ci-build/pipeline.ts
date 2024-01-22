#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { PipelineStack } from './pipeline-stack';

const app = new cdk.App();
new PipelineStack(app, 'PipelineStack', {
  env: { account: process.env.AWS_ACCOUNT_ID, region: process.env.AWS_REGION},
});
