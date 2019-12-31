FROM python:3.7-slim

ENV PYTHONUNBUFFERED=1
ENV ROOT=/usr/src/app

WORKDIR ${ROOT}

COPY docker/frontend/production/entrypoint.sh entrypoint.sh

COPY stilio/config.py stilio/config.py
COPY stilio/__init__.py stilio/__init__.py
COPY stilio/frontend stilio/frontend
COPY stilio/persistence stilio/persistence

RUN apt-get update \
    && apt-get install -y build-essential

RUN pip install pipenv
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --system
RUN rm -rf /Pipfile \
    && rm -rf /Pipfile.lock

RUN apt-get remove -y build-essential \
    && apt-get -y autoremove

ENTRYPOINT ["bash", "entrypoint.sh"]
