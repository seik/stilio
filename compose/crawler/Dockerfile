FROM python:3.7-slim

ENV PYTHONUNBUFFERED=1
ENV ROOT=/usr/src/app

WORKDIR ${ROOT}

COPY stilio/config.py stilio/config.py
COPY stilio/__init__.py stilio/__init__.py
COPY stilio/crawler stilio/crawler
COPY stilio/persistence stilio/persistence

COPY compose/crawler/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY compose/crawler/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY Pipfile .
COPY Pipfile.lock .

# FIXME remove all this making the crawler only install things it needs from Pipfile
# break pipfile into crawler/frontend
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential postgresql-server-dev-all \
    && pip install pipenv \
    && pipenv lock --requirements > requirements.txt \
    && pip install -r requirements.txt \
    && apt-get remove -y build-essential postgresql-server-dev-all \
    && apt-get -y autoremove

ENTRYPOINT ["/entrypoint"]