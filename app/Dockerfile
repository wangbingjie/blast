FROM python:3.8
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 gfortran libhealpix-cxx-dev -y

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./debug/debug_ipython.py /root/.ipython/profile_default/startup/

RUN mkdir /app
RUN mkdir /cutout_cdn
RUN mkdir /ghost_output
RUN mkdir /fsps

RUN
COPY . /app
WORKDIR /app
