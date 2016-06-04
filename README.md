# Hashiconf preparation

## Architecture

### Node1 :
* Docker
* XLD?
* Swarm Manager

### Node2 :
* Docker
* Gitlab

### Node3 :
* Docker
* Jenkins

## Commands


### Create a swarm docker :
```
docker run --rm swarm create
```

Current token : a782b857dbebc08ece503392671b95eb

### Start DOcker daemon listening to outside world (unsecure)

```
nohup sudo docker daemon -H unix:///var/run/docker.sock -H tcp://0.0.0.0:2376 & 2>&1 > logs
```


### Start Manager node (unsecure)

```
docker run -d -p 3376:3376 -t swarm manage -H 0.0.0.0:3376 token://a782b857dbebc08ece503392671b95eb
```

### Start Agent node (unsecure)

```
docker run -d swarm join --addr=<agent_ip>:2376 token://a782b857dbebc08ece503392671b95eb

```

### Control the manager from anywhere

```
export DOCKER_HOST=<manager_ip>:3376
```

### Basic GitLab :

```
docker run --detach --hostname <blah> --publish 443:443 --publish 80:80 --name gitlab --restart always gitlab/gitlab-ce:latest
```

### Issues :


No route to host on node 3?
No TLS so far
Accessing gitlab through node2.finaxys.com does not work, but IP do

### Generate TLS certificate :

First, the CA. CN set as finaxys.com

```
openssl genrsa -aes256 -out ca-key.pem 4096
openssl req -new -x509 -days 365 -key ca-key.pem -sha256 -out ca.pem
```

Stored in node1, passphrase in keepass

Then, 3 private keys + csr for each node :
```
openssl genrsa -out nodeX-key.pem 4096
openssl req -subj "/CN=nodeX.finaxys.com" -sha256 -new -key nodeX-key.pem -out nodeX.csr
```

Then add IP adress connection :
```
echo subjectAltName = IP:178.33.83.16X,IP:127.0.0.1 > extfileX.cnf
openssl x509 -req -days 365 -sha256 -in node1.csr -CA ca.pem -CAkey ca-key.pem \
  -CAcreateserial -out node1-cert.pem -extfile extfile1.cnf
```


