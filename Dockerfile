FROM python:3.9-slim-bullseye

RUN apt-get update -y
RUN apt-get install gcc -y
RUN apt-get install nano -y

RUN mkdir /usr/src/mt4-postgresql-connector/
WORKDIR /usr/src/mt4-postgresql-connector/

RUN mkdir requirements
COPY ./requirements.txt requirements/requirements.txt

RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir -r requirements/requirements.txt

ADD . /usr/src/mt4-postgresql-connector/

EXPOSE 8000