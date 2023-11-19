#!/bin/bash -x
kubectl label pod $POD_NAME inferencepod=$POD_NAME
service_name=$POD_NAME-svc-$(kubectl get no -o wide `kubectl  get po  $POD_NAME -o wide | awk '{print $7}'|grep -v NODE`| awk '{print $7}' | grep -v EXTERNAL-IP|sed "s/\./-/g")
export SVC_NAME=$service_name
cat /node_port_svc_template.yaml | envsubst | kubectl apply -f - 
