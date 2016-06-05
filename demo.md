# Demo scenario

## The Cluster

First, launch the cluster.

You need :
* A consul server somewhere
* Docker engines with a KV store pointing to the Consul server defined above
* Launch the script swarm-multihost.sh. It will create a swarm manager and two nodes.

You can also do that using docker machines, it will probably be much easier.


## The SF

Once the swarm cluster is up, launch the software factory.

    docker-compose up -d

in the folder ./sf

Check the docker compose file for details, but basically it should pop :
* Gitlab on port 80/443
* Jenkins on port 8080
* Artifactory on port 8081

## Configuration

Once the SF is up, it needs to be configured.

### Gitlab

On Gitlab, create the admin password, then a simple user.
Once it is done, create a basic repository.

	You can git clone with the IP address of the node it is on (with HTTP)

### Artifactory

On Artifactory, you need a license. (see mails)
Once done, create a repository for docker images.

### Jenkins

On Jenkins, it is Free for All from the start.

Activate the Gitlab plugin, by putting all the hpi files in the folder

/var/jenkins_home/plugins

Create a job freestyle. That builds each time anything happens to the repository
