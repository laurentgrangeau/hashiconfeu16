FROM jenkins:alpine

COPY plugins.txt /usr/share/jenkins/ref/

COPY docker-compose /usr/bin/

RUN /usr/local/bin/plugins.sh /usr/share/jenkins/ref/plugins.txt


