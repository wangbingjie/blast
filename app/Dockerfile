FROM hub.ncsa.illinois.edu/blast/deps@sha256:0fe60eb8fee7c93664ee67e2b82fab048311f2bdf574011a402ca656f9e1408d as deps

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

RUN pip install --no-cache-dir watchdog

RUN mkdir /app
COPY . /app
WORKDIR /app
