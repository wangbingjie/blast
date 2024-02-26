FROM python:3.11
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 gfortran libhealpix-cxx-dev libhdf5-serial-dev netcdf-bin libnetcdf-dev -y

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./debug/debug_ipython.py /root/.ipython/profile_default/startup/

RUN mkdir /app
RUN mkdir /data
RUN mkdir /data/cutout_cdn
RUN mkdir /data/sed_output
RUN mkdir /ghost_output
RUN mkdir /fsps
RUN mkdir /sbipp_phot

RUN cd /sbipp_phot
RUN curl -LJO https://zenodo.org/records/10703208/files/sbi_phot_global.h5
RUN curl -LJO https://zenodo.org/records/10703208/files/sbi_phot_local.h5
RUN cd /
### RUN mv sbi_phot_global.h5 /sbipp_phot/
### RUN mv sbi_phot_local.h5 /sbipp_phot/

RUN
COPY . /app
WORKDIR /app
