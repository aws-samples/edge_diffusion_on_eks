#!/bin/bash -x
#restore simulator state from SQS in the case of previous run
sqs_file="/tmp/"$RANDOM".json"
aws sqs receive-message --queue-url ${QUEUE_URL} > $sqs_file
echo "sqs exit code="$?
if (( $?>0 ))
then
  echo "ERR-SQS"
  j=0
else
  receipt_handle=`cat $sqs_file | jq '.Messages[].ReceiptHandle'|sed 's/"//g'`
  j=`cat $sqs_file | jq '.Messages[].Body'|sed 's/"//g'`
  if [ -z "$j" ]
  then
    echo "EMPTY-SQS"
    j=0
  else
    aws sqs delete-message --queue-url ${QUEUE_URL} --receipt-handle $receipt_handle
  fi
fi
rm -f $sqs_file

prev_clients=0

#simulator sine wave range. From $j to 3.14 in 0.1 increments
_seq=`seq $j $RADIAN_INTERVAL $RADIAN_MAX`
#_seq=`seq 0.01 0.168 3.14`
echo "first seq is "$_seq
while true; do
for i in $_seq; do
  sqs_file="/tmp/"$RANDOM".json"
  aws sqs receive-message --queue-url ${QUEUE_URL} > $sqs_file
  if (( $?<=0 )); then
    receipt_handle=`cat $sqs_file | jq '.Messages[].ReceiptHandle'|sed 's/"//g'`
    if [ -n "$receipt_handle" ]; then
      echo "delete msg receipt_handle="$receipt_handle
      aws sqs delete-message --queue-url ${QUEUE_URL} --receipt-handle $receipt_handle
    fi
  fi
  rm -f $sqs_file
  x=`echo $i|awk '{print $1}'`
  sinx=`echo $i|awk '{print int(sin($1)*100)}'`
  echo "sinx=" $sinx
  echo "i=" $i
  aws sqs send-message --queue-url ${QUEUE_URL} --message-body "$i"

  clients=`echo $(( (sinx * $CLIENT_SCALE_RATIO) + $MIN_AT_CYCLE_START ))`

  kubectl scale -n $CLIENT_DEPLOY_NS deploy/$CLIENT_DEPLOY_PREFIX --replicas=$clients
  aws cloudwatch put-metric-data --metric-name app_workers --namespace ${DEPLOY_NAME} --value ${clients}
  echo "app_workers(clients)="$clients" sinx="$sinx

  prev_clients=$clients
  sleeptime=`awk -v min=$MIN_SLEEP_BETWEEN_CYCLE -v max=$MAX_SLEEP_BETWEEN_CYCLE 'BEGIN{srand(); print int(min+rand()*(max-min+1))}'`
  echo "cleanning not ready nodes and faulty pods"
  kubectl delete po `kubectl get po | egrep 'Evicted|CrashLoopBackOff|CreateContainerError|ExitCode|OOMKilled|RunContainerError'|awk '{print $1}'`
  sleep $sleeptime"m"
done
#longer cycle _seq=`seq 0.01 0.021 3.14`
j=0
_seq=`seq $j $RADIAN_INTERVAL $RADIAN_MAX`
#_seq=`seq 0.01 0.168 3.14`
echo "new cycle "$_seq
done
