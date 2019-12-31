FROM python:3.7-slim

ENV PYTHONUNBUFFERED=1
ENV ROOT=/usr/src/app

WORKDIR ${ROOT}

COPY . ${ROOT}

RUN apt-get update \
    && apt-get install -y build-essential

RUN pip install pipenv
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --system --dev
RUN rm -rf /Pipfile \
    && rm -rf /Pipfile.lock

RUN apt-get remove -y build-essential \
    && apt-get -y autoremove
