FROM python:3.8

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
#RUN apt-get update
#RUN apt-get install -y --no-install-recommends gcc libc-dev python3-dev default-libmysqlclient-dev
#RUN apt-get install -y gcc
#RUN apt-get -y install default-libmysqlclient-dev
RUN pip install -r /requirements.txt
RUN mkdir /app
COPY . /app
WORKDIR /app


#FROM python:3.8-slim-buster
#WORKDIR app/
#COPY requirements.txt requirements.txt
#RUN pip3 install -r requirements.txt
#COPY . .
#CMD python3 manage.py test host.tests -v 2; python3 manage.py runserver 0.0.0.0:8000
#CMD ["python3", "manage.py", "test", "host.tests", "-v 2"]
#CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

#FROM python:3.8-slim-buster AS base
#WORKDIR /app
#COPY requirements.txt /app
#RUN pip3 install -r requirements.txt

#FROM base as src
#COPY . /app

#FROM src as test
#COPY requirements.txt /app
#RUN pip3 install -r requirements.txt
#RUN python3 manage.py test host.tests -v 2

#FROM src as prod
#ENTRYPOINT ["python3"]
#CMD ["manage.py", "runserver", "0.0.0.0:8000"]
