#!/bin/bash
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
if [ -z "$TOKEN" ]
then
  echo "No token for IMDS_v2 - check /api/token url"
  exit
fi
NODE=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" 169.254.169.254/latest/meta-data/local-hostname)
if [ -z "$NODE" ]
then
  echo "No node name - check /meta-data/local-hostname"
  exit
fi
echo "NODE="$NODE
INSTANCE_TYPE=$(kubectl get no $NODE -L node.kubernetes.io/instance-type | grep -v NAME| awk '{print $NF}')
if [ -z "$INSTANCE_TYPE" ]
then
  echo "No instance type"
  exit
fi
echo INSTANCE_TYPE=$INSTANCE_TYPE
echo aws cloudwatch put-metric-data --metric-name $INSTANCE_TYPE --namespace spot-sig --value 1 
aws cloudwatch put-metric-data --metric-name $INSTANCE_TYPE --namespace spot-sig --value 1 
echo "cloudwatch exit code="$?
if (( $?>0 ))
then
  echo "ERR-CW"
fi


POLL_INTERVAL=${POLL_INTERVAL:-5}
NOTICE_URL=${NOTICE_URL:-http://169.254.169.254/latest/meta-data/events/recommendations/rebalance}

echo "Polling ${NOTICE_URL} every ${POLL_INTERVAL} second(s)"

while http_status=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" -o /dev/null -w '%{http_code}' -sL ${NOTICE_URL}); [ ${http_status} -ne 200 ]; do
  echo $(date): ${http_status}
  sleep ${POLL_INTERVAL}
done

echo $(date): ${NOTICE_URL}
echo $(date): ${http_status}

echo aws cloudwatch put-metric-data --metric-name rebalance --namespace spot-sig --value 1 --dimensions node=$NODE
aws cloudwatch put-metric-data --metric-name rebalance --namespace spot-sig --value 1 --dimensions node=$NODE

echo "Draining the nodei due to spot rebalance recommendations."
kubectl drain $NODE --force --ignore-daemonsets --delete-emptydir-data
