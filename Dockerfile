FROM python:3.10-slim as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --only main

FROM python:3.10-slim

# set working directory
WORKDIR .

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy lock-file
COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

# install python dependencies
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# add app
COPY . .
