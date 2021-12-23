# blast
Django web app for the automatic characterization of supernova hosts

![Main Branch CI](https://github.com/astrophpeter/blast/workflows/Main%20Branch%20CI/badge.svg?branch=main) 
[![Documentation Status](https://readthedocs.org/projects/blast/badge/?version=latest)](https://blast.readthedocs.io/en/latest/?badge=latest)

Read the documentation at [https://blast.readthedocs.io/en/latest/](https://blast.readthedocs.io/en/latest/)

## Running locally
1. Install the [Docker desktop app](https://www.docker.com/products/docker-desktop)
2. Open up the command line and pull the Docker image of the lastest commit on main:

`$ docker pull ghcr.io/astrophpeter/blast:edge`

3. Run the image and make blast visible to your machine on port 8000:

`$ docker run --publish 8000:8000 image_ID`

where you can find image_ID in the Docker Desktop app or by running `$ docker images`

4. Got to [localhost:8000/host/](localhost:8000/host/) in your browser

