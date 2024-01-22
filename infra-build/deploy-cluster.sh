#!/bin/bash

npm install aws-cdk-lib@2.115.0
npm i @aws-quickstart/eks-blueprints@1.13.1
. ~/.bash_profile
cdk bootstrap aws://$AWS_ACCOUNT_ID/$AWS_REGION
npm install
cdk deploy --app "npx ts-node --prefer-ts-exts ./eks-cluster.ts" --all 
