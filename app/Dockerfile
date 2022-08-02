FROM python:3.8
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 libhealpix-cxx-dev gfortran -y

COPY ./requirements.txt /requirements.txt
RUN export SPS_HOME=/fsps
RUN pip install -r /requirements.txt

RUN mkdir /app
RUN mkdir /cutout_cdn
RUN mkdir /ghost_output
COPY . /app
WORKDIR /app
