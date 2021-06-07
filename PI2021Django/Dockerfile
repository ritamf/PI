FROM python:3.8-alpine

ENV PATH="/scripts:${PATH}"

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers
RUN apk add --no-cache git
ARG CASS_DRIVER_NO_CYTHON="1"
ARG CASS_DRIVER_BUILD_CONCURRENCY="8"
RUN pip install -r /requirements.txt
RUN apk del .tmp

RUN mkdir /Project
COPY ./Project /Project
RUN mkdir /templates
COPY ./templates /templates
RUN mkdir /webapp
COPY ./webapp /webapp
RUN mkdir /scripts
COPY ./scripts /scripts

RUN chmod -x /scripts/*

CMD ["entrypoint.sh"]
