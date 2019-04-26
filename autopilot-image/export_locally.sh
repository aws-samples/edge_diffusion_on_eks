#!/bin/bash

export QUEUE_URL="https://sqs.us-west-2.amazonaws.com/356566070122/gameserver.fifo"
export NAMESPACE="default"
export POD_NAME="my_pod"
export DEPLOY_NAME="minecraft"
export CURRENT_SIZE_METRIC_NAME="current_size"
export NEW_SIZE_METRIC_NAME="new_size"
export SLEEP_TIME_B4_NEXT_READ="10"
