FROM python:3.5

ADD . /minitwit

WORKDIR /minitwit

RUN apt-get update && apt-get install -y libpq-dev gcc && pip3 install -r requirements.txt

ENV FLASK_APP=minitwit.py LC_ALL=C.UTF-8 LANG=C.UTF-8

EXPOSE 5000

CMD flask run --host=0.0.0.0
