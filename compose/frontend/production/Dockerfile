FROM python:3.7-slim

ENV PYTHONUNBUFFERED=1
ENV ROOT=/usr/src/app

WORKDIR ${ROOT}

COPY stilio/config.py stilio/config.py
COPY stilio/__init__.py stilio/__init__.py
COPY stilio/frontend stilio/frontend
COPY stilio/persistence stilio/persistence

COPY Pipfile .
COPY Pipfile.lock .

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential postgresql-server-dev-all \
    && pip install pipenv \
    && pipenv lock --requirements > requirements.txt \
    && pip install -r requirements.txt \
    && apt-get remove -y build-essential postgresql-server-dev-all \
    && apt-get -y autoremove

ENTRYPOINT ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "stilio.frontend.main:app"]