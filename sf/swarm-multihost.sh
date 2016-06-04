#!/bin/bash

NODE1_IP="178.33.83.161"
NODE2_IP="178.33.83.162"
NODE3_IP="178.33.83.163"
NODE1="-H tcp://${NODE1_IP}:2376"
NODE2="-H tcp://${NODE2_IP}:2376"
NODE3="-H tcp://${NODE3_IP}:2376"

docker ${NODE1} run --name consul-master -d --net=host -e 'CONSUL_LOCAL_CONFIG={"skip_leave_on_interrupt": true}' consul agent -server -bind=${NODE1_IP} -client=${NODE1_IP} -bootstrap
sleep 5
docker ${NODE1} run --name swarm-manager -d -p 3376:3376 swarm manage -H tcp://0.0.0.0:3376  consul://${NODE1_IP}:8500
docker ${NODE1} run --name swarm-slave1 -d swarm join --addr=${NODE1_IP}:2376 consul://${NODE1_IP}:8500
docker ${NODE2} run --name swarm-slave2 -d swarm join --addr=${NODE2_IP}:2376 consul://${NODE1_IP}:8500
docker ${NODE3} run --name swarm-slave3 -d swarm join --addr=${NODE3_IP}:2376 consul://${NODE1_IP}:8500
