FROM python:3.5

ADD . /minitwit

WORKDIR /minitwit

RUN pip install -r requirements.txt

ENV FLASK_APP minitwit.py

RUN flask initdb

EXPOSE 5000

CMD flask run --host=0.0.0.0
