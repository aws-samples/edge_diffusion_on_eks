* Exec the following:
```bash
npm uninstall -g aws-cdk
npm install -g aws-cdk
```
* Export the following variables
```bash
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --output text --query Account)
export AWS_REGION=us-west-2
export CF_STACK=yahavb-cdk-k8s
export CLUSTER=test5
```
