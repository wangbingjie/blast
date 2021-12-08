#FROM python:3.8-slim-buster
#WORKDIR app/
#COPY requirements.txt requirements.txt
#RUN pip3 install -r requirements.txt
#COPY . .
#CMD python3 manage.py test host.tests -v 2; python3 manage.py runserver 0.0.0.0:8000
#CMD ["python3", "manage.py", "test", "host.tests", "-v 2"]
#CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

FROM python:3.8-slim-buster AS base
WORKDIR web_app/
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

FROM base as src
COPY . .

FROM src as test
COPY requirements.txt web_app/
RUN pip3 install -r requirements.txt
RUN python3 manage.py test host.tests

FROM src as prod
ENTRYPOINT ["python3"]
CMD ["manage.py", "runserver", "0.0.0.0:8000"]