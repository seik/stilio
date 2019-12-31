#!/bin/sh

set -o errexit
set -o nounset

gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 stilio.frontend.main:app
