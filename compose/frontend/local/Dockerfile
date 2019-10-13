FROM python:3.7-slim

ENV PYTHONUNBUFFERED=1
ENV ROOT=/usr/src/app

WORKDIR ${ROOT}

COPY . ${ROOT}

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

ENTRYPOINT ["uvicorn", "stilio.frontend.main:app", "--reload", "--host", "0.0.0.0"]