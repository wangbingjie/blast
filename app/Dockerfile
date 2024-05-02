FROM hub.ncsa.illinois.edu/blast/deps@sha256:c402391fa2490e6c56518084c4469f9dc23bb4a6691645bd0a1cc491e05d2f94 as deps

FROM python:3.11
ENV PYTHONUNBUFFERED 1

RUN apt-get update && DEBIAN_FRONTEND=noninteractive && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    gfortran \
    libhealpix-cxx-dev \
    libhdf5-serial-dev \
    netcdf-bin \
    libnetcdf-dev \
    && rm -rf /var/lib/apt/list/*

COPY ./debug/debug_ipython.py /root/.ipython/profile_default/startup/

COPY --from=deps /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=deps /usr/local/bin/ /usr/local/bin/

RUN pip install --no-cache-dir watchdog django-celery-results

RUN mkdir /app
COPY . /app
WORKDIR /app
