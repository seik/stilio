FROM python:3.7-alpine3.9

ENV PYTHONUNBUFFERED=1
ENV ROOT=/usr/src/app

WORKDIR ${ROOT}

COPY stilio/config.py stilio/config.py
COPY stilio/__init__.py stilio/__init__.py
COPY stilio/frontend stilio/frontend
COPY stilio/persistence stilio/persistence

COPY Pipfile .
COPY Pipfile.lock .

RUN apk add --update --no-cache --virtual .build-deps build-base gcc musl-dev git \
    && pip install --upgrade pip setuptools wheel pipenv \
    && pipenv install \
    && apk del .build-deps build-base gcc musl-dev git

ENTRYPOINT ["pipenv", "run", "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:80", "stilio.frontend.main:app"]