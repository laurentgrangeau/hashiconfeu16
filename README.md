# Hashiconf preparation

## Architecture

### Node1 :
* Docker with consul backend
* Swarm Manager
* Swarm Slave 1

### Node2 :
* Docker with consul backend
* Swarm Slave 2

### Node3 :
* Docker regular (to bootstrap consul)
* Consul server

## Commands

### Setting up the swarm with consul

First, launch a consul cluster somewhere (Node 3). It must be done before 
setting up swarm because swarm will rely on that.

Command line :

    docker run -d --net=host -e 'CONSUL_LOCAL_CONFIG={"skip_leave_on_interrupt": true}' consul agent -server -bind=178.33.83.163 -client=178.33.83.163 --boostrap


Once it is done, launch the docker daemons on the machines for swarm (Node 1, 2)
 with :

   nohup sudo docker daemon -H unix:///var/run/docker.sock -H tcp://0.0.0.0:2376 --cluster-store consul://178.33.83.163:8500 --cluster-advertise eth1:2376 --label==front &

   nohup sudo docker daemon -H unix:///var/run/docker.sock -H tcp://0.0.0.0:2376 --cluster-store consul://178.33.83.163:8500 --cluster-advertise eth1:2376 --label==back &


Launch the script swarm-multihost.sh in the folder sf

### Starting the SF

docker-compose up in the sf folder.

check where they are deployed.

### Control the swarm

```
export DOCKER_HOST=<manager_ip>:3376
```

### Basic GitLab :

```
docker run --detach --hostname <blah> --publish 443:443 --publish 80:80 --name gitlab --restart always gitlab/gitlab-ce:latest
```

### Issues :

No TLS so far
Accessing gitlab through node2.finaxys.com does not work, but IP do
