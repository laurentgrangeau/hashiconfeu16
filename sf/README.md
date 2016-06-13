# Software factory

## Components

* Gitlab
* Jenkins

## Set up Gitlab

1. Create admin account
2. Create regular account named _chris_
3. Create project _minitwit_
4. ```git clone http://<IP_DOCKER_MACHINE>:80/chris/minitwit``
5. Cp the content of app/ into the cloned repo

## Set up jenkins job

6. Before pushing anything, go on jenkins and create a project named _minitwit-continuous_
  * Source code version : Git
    * Repo ULR : http://sf_gitlab_1/chris/minitwit.git
    * Credentials : Add them. user password, _chris_
  * Tick _Build when a change is pushed to GitLab._. Keep the address given somewhere.
  * Build : execute a shell script
    ```
    export DOCKER_HOST=<swarm_manager_ip>:3376
    docker-compose down
    docker-compose up --build -d
    ```

## Finish Gitlab setup

7. Get the adress given in Jenkins, go in GitLa/Project/Settings/Webhooks
8. Add a webhook :
  * URL : Given, by jenkins, probably : http://sf_jenkins_1:8080/project/minitwit-continuous
  * SSL : deactivated

## Test it now

9. COmmit everything in the repo minitwit, and push it. You should see it being built and deployed automatically


* Artifactory
