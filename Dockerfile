FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get -y upgrade
RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip install -r requirements.txt
