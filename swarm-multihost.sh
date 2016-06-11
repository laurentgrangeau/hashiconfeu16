#!/bin/bash

NODE1_IP="178.33.83.161"
NODE2_IP="178.33.83.162"
NODE3_IP="178.33.83.163"
NODE1="-H tcp://${NODE1_IP}:2376"
NODE2="-H tcp://${NODE2_IP}:2376"
NODE3="-H tcp://${NODE3_IP}:2376"

docker ${NODE1} run --name swarm-manager -d -p 3376:3376 swarm manage -H tcp://0.0.0.0:3376  consul://${NODE3_IP}:8500
docker ${NODE1} run --name swarm-slave1 -d swarm join --addr=${NODE1_IP}:2376 consul://${NODE3_IP}:8500
docker ${NODE2} run --name swarm-slave2 -d swarm join --addr=${NODE2_IP}:2376 consul://${NODE3_IP}:8500
