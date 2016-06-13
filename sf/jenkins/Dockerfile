FROM jenkins:latest

COPY plugins.txt /usr/share/jenkins/ref/

USER root
COPY docker-compose /usr/bin/
RUN chmod 777 /usr/bin/docker-compose
USER jenkins

RUN /usr/local/bin/plugins.sh /usr/share/jenkins/ref/plugins.txt


