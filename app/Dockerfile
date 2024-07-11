FROM hub.ncsa.illinois.edu/blast/deps:20240711 AS deps

FROM python:3.11
ENV PYTHONUNBUFFERED=1

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

# Temporary solution to install modified astro_ghost package until changes are merged upstream
RUN git clone https://github.com/manning-ncsa/astro_ghost.git /tmp/blast && cd /tmp/blast && \
    git checkout c3e9baf7e537a2b2294fbb9763017438e86ee8ef && \
    pip uninstall --yes astro_ghost && pip install --no-cache-dir . && \
    cd / && rm -rf /tmp/blast

RUN mkdir /app
COPY . /app
WORKDIR /app
