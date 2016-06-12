#!/bin/bash

set -e

docker-machine create -d virtualbox swarm-node1
docker-machine create -d virtualbox swarm-node2
docker-machine create -d virtualbox swarm-node3

docker "$(docker-machine config swarm-node3)" run -d --net=host -e 'CONSUL_LOCAL_CONFIG={"skip_leave_on_interrupt": true}' consul agent -server -bind=$(docker-machine ip swarm-node3) -client=$(docker-machine ip swarm-node3) --boostrap

docker "$(docker-machine config swarm-node1)" run --name swarm-manager -d -p 3376:3376 swarm manage -H tcp://0.0.0.0:3376  consul://$(docker-machine ip swarm-node3):8500
docker "$(docker-machine config swarm-node1)" run --name swarm-slave1 -d swarm join --addr=$(docker-machine ip swarm-node1):2376 consul://$(docker-machine ip swarm-node3):8500
docker "$(docker-machine config swarm-node2)" run --name swarm-slave2 -d swarm join --addr=$(docker-machine ip swarm-node2):2376 consul://$(docker-machine ip swarm-node3):8500