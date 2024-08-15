FROM python:3.10

## Install Python dependencies
COPY docs/requirements.txt /tmp/docs-requirements.txt
RUN pip install --no-cache-dir -r /tmp/docs-requirements.txt
COPY app/requirements.txt /tmp/app-requirements.txt 
RUN pip install --no-cache-dir -r /tmp/app-requirements.txt

RUN pip install --no-cache-dir django-latexify
RUN pip install --no-cache-dir photutils
