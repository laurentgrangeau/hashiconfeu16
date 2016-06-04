#!/bin/bash

NODE1_IP="178.33.83.161"
NODE2_IP="178.33.83.162"
NODE3_IP="178.33.83.163"
NODES="${NODE1_IP}
${NODE2_IP}"

echo "L'apocalypse a commencé !"

for node in $NODES
do
  echo "${node}"
  DOCKER_STRING="-H tcp://${node}:2376"
  RUNNING=`docker ${DOCKER_STRING} ps -q`
  docker ${DOCKER_STRING} kill ${RUNNING}
  docker ${DOCKER_STRING} rm ${RUNNING}
done
