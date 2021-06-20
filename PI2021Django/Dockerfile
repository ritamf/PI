FROM python:3.9.5-alpine3.13

ENV PATH="/scripts:${PATH}"

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers
RUN apk add git py3-cassandra-driver --update-cache --repository http://dl-3.alpinelinux.org/alpine/edge/testing/
ARG CASS_DRIVER_NO_CYTHON="1"
ARG CASS_DRIVER_BUILD_CONCURRENCY="8"
RUN pip install -U -r /requirements.txt
RUN apk del .tmp

COPY manage.py /manage.py
RUN mkdir /Project
COPY ./Project /Project
RUN mkdir /templates
COPY ./templates /templates
RUN mkdir /webapp
COPY ./webapp /webapp
RUN mkdir /scripts
COPY ./scripts /scripts
RUN mkdir /static
RUN mkdir /staticfiles
RUN mkdir /proxy

RUN chmod -x /scripts/*