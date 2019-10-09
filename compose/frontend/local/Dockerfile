FROM python:3.7-alpine3.9

ENV PYTHONUNBUFFERED=1
ENV ROOT=/usr/src/app

WORKDIR ${ROOT}

COPY . ${ROOT}

COPY Pipfile .
COPY Pipfile.lock .

# FIXME remove all this making the crawler only install things it needs from Pipfile
# break pipfile into crawler/frontend
RUN apk add --update --no-cache --virtual .build-deps build-base gcc musl-dev git \
    && pip install --upgrade pip setuptools wheel pipenv \
    && pipenv install \
    && apk del .build-deps build-base gcc musl-dev git

ENTRYPOINT ["pipenv", "run", "uvicorn", "stilio.frontend.main:app", "--reload", "--host", "0.0.0.0"]