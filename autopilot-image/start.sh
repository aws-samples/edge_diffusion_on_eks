#!/bin/sh -x
#source ./export_locally.sh
echo "Starting the game server auto-pilot"

# This process runs as daemon set per game server deployment. It attempt to get the required number of game-servers within a region.
# It gets this number from an ML model. For testing purpose, it avoids the ML endpoint and uses random numbers instead. 
# In the case of scale down, individual game server pods should protect itself with a termination grace period to avoid player interruption 
# In such cases, an extra x min will be given where terminated pods status will turn to 'terminating'. 
# Game servers can listen to SIGKILL or SIGTERM and trigger a game-server drain (this is not k8s thing. it is a game-server logic)

if [ "${QUEUE_URL}" == "" ]; then
  echo '[ERROR] Environment variable `QUEUE_URL` has no value set.' 1>&2
  exit 1
fi

if [ "${NAMESPACE}" == "" ]; then
  echo '[ERROR] Environment variable `NAMESPACE` has no value set.' 1>&2
  exit 1
fi

if [ "${POD_NAME}" == "" ]; then
  echo '[ERROR] Environment variable `POD_NAME` has no value set.' 1>&2
  exit 1
fi

if [ "${DEPLOY_NAME}" == "" ]; then
  echo '[ERROR] Environment variable `DEPLOY_NAME` has no value set.' 1>&2
  exit 1
fi

if [ "${CURRENT_SIZE_METRIC_NAME}" == "" ]; then
  echo '[ERROR] Environment variable `CURRENT_SIZE_METRIC_NAME` has no value set.' 1>&2
  exit 1
fi

if [ "${NEW_SIZE_METRIC_NAME}" == "" ]; then
  echo '[ERROR] Environment variable `NEW_SIZE_METRIC_NAME` has no value set.' 1>&2
  exit 1
fi

if [ "${FREQUENCY}" == "" ]; then
  echo '[ERROR] Environment variable `FREQUENCY` has no value set.' 1>&2
  exit 1
fi

while true
do

  #Testing only - generating random size for replica set. Realworld solution will get this number from an AI/ML endpoint
  NEW_RS_SIZE=$RANDOM
  RANGE=30
  let "NEW_RS_SIZE %= $RANGE"
  echo NEW_RS_SIZE=${NEW_RS_SIZE}
  #End testing section

  #Getting predictions from a trained model
  MODEL_URL="https://gf8nwoay7d.execute-api.us-west-2.amazonaws.com/api/predict"
  MODEL_URL_PARAM="ap-northeast-1"
  NEW_RS_SIZE_FLOAT=`curl -w "\n" $MODEL_URL/$MODEL_URL_PARAM | jq '.Prediction.num_of_gameservers'`
  NEW_RS_SIZE=${NEW_RS_SIZE_FLOAT%.*}
  echo $NEW_RS_SIZE

  CURRENT_RS_SIZE=`kubectl get deploy ${DEPLOY_NAME} -n ${NAMESPACE} -o=jsonpath='{.status.availableReplicas}'`
  echo CURRENT_RS_SIZE=${CURRENT_RS_SIZE}

  kubectl scale deploy/${DEPLOY_NAME} --replicas=${NEW_RS_SIZE} -n ${NAMESPACE}
  echo "sleeping for ${SLEEP_TIME_B4_NEXT_READ} to allow the scale operations"

  MESSAGE="[{'type': 'autopilot','deployment':${DEPLOY},'current_rs_size': ${CURRENT_RS_SIZE},'new_rs_size':${NEW_RS_SIZE},'region':'us-west-2'}]"
  MESSAGE_GRP_ID="gsGrp_us-west-2"
  aws sqs send-message --queue-url ${QUEUE_URL} --message-body "${MESSAGE}" --message-group-id ${MESSAGE_GRP_ID}
  aws cloudwatch put-metric-data --metric-name ${CURRENT_SIZE_METRIC_NAME} --namespace ${DEPLOY_NAME} --value ${CURRENT_RS_SIZE}
  aws cloudwatch put-metric-data --metric-name ${NEW_SIZE_METRIC_NAME} --namespace ${DEPLOY_NAME} --value ${NEW_RS_SIZE}

  sleep ${FREQUENCY}

done
