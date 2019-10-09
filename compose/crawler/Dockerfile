FROM python:3.7-alpine3.8

ENV PYTHONUNBUFFERED=1
ENV ROOT=/usr/src/app

WORKDIR ${ROOT}

COPY stilio/config.py stilio/config.py
COPY stilio/__init__.py stilio/__init__.py
COPY stilio/crawler stilio/crawler
COPY stilio/persistence stilio/persistence

COPY Pipfile .
COPY Pipfile.lock .

# FIXME remove all this making the crawler only install things it needs from Pipfile
# break pipfile into crawler/frontend
RUN apk add --no-cache --virtual .build-deps build-base gcc musl-dev git \
    && pip install --upgrade pip setuptools wheel pipenv \
    && pipenv install \
    && apk del .build-deps build-base gcc musl-dev git

ENTRYPOINT ["pipenv", "run", "python", "-m", "stilio.crawler.main"]