FROM python:3.7-alpine

WORKDIR /opt/bazinga

COPY requirements.txt .

RUN pip install -U -r requirements.txt

COPY bazinga-sdk/ .

ENTRYPOINT [ "kopf", "run", "secretz.py" ]