FROM python:3.5

ADD ./vault_init /vault_init

WORKDIR /vault_init

RUN pip install hvac

CMD python init.py
