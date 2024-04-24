FROM python:3.11 as mc

RUN curl https://dl.min.io/client/mc/release/linux-amd64/mc -o /usr/local/bin/mc && \
    chmod +x /usr/local/bin/mc

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
    rsync \
    && rm -rf /var/lib/apt/list/*

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt --no-cache-dir

COPY ./debug/debug_ipython.py /root/.ipython/profile_default/startup/

RUN mkdir /app

COPY . /app
WORKDIR /app

COPY --from=mc /usr/local/bin/mc /usr/local/bin/mc
