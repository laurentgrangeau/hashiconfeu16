#!/bin/bash

set -e

docker-machine rm kvstore-swarm
docker-machine rm swarm-master
docker-machine rm swarm-slave3
docker-machine rm swarm-slave2
docker-machine rm swarm-slave1