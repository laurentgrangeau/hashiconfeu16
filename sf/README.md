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
6. Before pushing anything, go on jenkins and create a project named _minitwit-continuous_
  * Source code version : Git
    * Repo ULR : http://sf_gitlab_1/chris/minitwit.git
    * Credentials : Add them. user password, _chris_
    * 


* Artifactory
