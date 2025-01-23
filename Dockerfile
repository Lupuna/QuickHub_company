FROM python:3.12-alpine3.20


COPY requirements.txt /temp/requirements.txt
COPY core /core
WORKDIR /core

RUN chmod +x entrypoint.sh

EXPOSE 8000

RUN apk add --no-cache curl

RUN apk add postgresql-client build-base postgresql-dev

RUN pip install -r /temp/requirements.txt
