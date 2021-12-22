FROM python:latest

WORKDIR /code

COPY . /code/

RUN pip install -r requirements.txt



