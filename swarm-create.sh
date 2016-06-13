#!/bin/bash

set -e

docker-machine create -d virtualbox kvstore-swarm
docker --tlsverify --tlscacert="C:\\Users\\Laurent Grangeau\\.docker\\machine\\certs\\ca.pem" --tlscert="C:\\Users\\Laurent Grangeau\\.docker\\machine\\certs\\cert.pem" --tlskey="C:\\Users\\Laurent Grangeau\\.docker\\machine\\certs\\key.pem" -H=tcp://$(docker-machine ip kvstore-swarm):2376 run -d -p "8500:8500" -h "consul" progrium/consul -server -bootstrap

docker-machine create -d virtualbox --swarm --swarm-master --swarm-discovery consul://$(docker-machine ip kvstore-swarm):8500 --engine-opt="cluster-store=consul://$(docker-machine ip kvstore-swarm):8500" --engine-opt="cluster-advertise=eth1:2376" swarm-master

docker-machine create -d virtualbox --swarm --swarm-discovery consul://$(docker-machine ip kvstore-swarm):8500 --engine-opt="cluster-store=consul://$(docker-machine ip kvstore-swarm):8500" --engine-opt="cluster-advertise=eth1:2376" --engine-label="environment=frontend" swarm-slave1
docker-machine create -d virtualbox --swarm --swarm-discovery consul://$(docker-machine ip kvstore-swarm):8500 --engine-opt="cluster-store=consul://$(docker-machine ip kvstore-swarm):8500" --engine-opt="cluster-advertise=eth1:2376" --engine-label="environment=backend" swarm-slave2
docker-machine create -d virtualbox --swarm --swarm-discovery consul://$(docker-machine ip kvstore-swarm):8500 --engine-opt="cluster-store=consul://$(docker-machine ip kvstore-swarm):8500" --engine-opt="cluster-advertise=eth1:2376" --engine-label="environment=sf" swarm-slave3