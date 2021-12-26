Installing blast locally
++++++++++++++++++++++++

There are several ways to install and run blast locally. You might want to
do this if you want to contribute to the development of blast, or if you don't
want to use the live web app. This pages walks you through how to install blast
and get it running on your machine in a couple of different ways.

Docker
======

The first (and recomended) option for installing and running blast locally is to
use docker.

Install the Docker desktop app
-------------------------------

The first step is to install the docker desktop application, which can be found
`here <https://docs.docker.com/get-docker/>`_ for mac, windows, and linux based
systems.

Pull the docker image
---------------------------------

Open up the command line and pull the most recent Docker image of the lastest
commit on main

.. code:: none

    docker pull ghcr.io/astrophpeter/blast:edge

Run the docker image
--------------------

Run the image and make blast visible to your machine on port 8000

.. code:: none

    docker run --publish 8000:8000 image_ID

You can find image_ID in the Docker Desktop app or by running ``docker images``.
Then got to `localhost:8000/host/ <localhost:8000/host/>`_ in your web browser
and blast should be running.

Native install
==============

The other option to install blast is a native install. The recommended way to do
this is to create an isolated python environment and then install all the required
packages within that environment.

Conda
-----

.. code:: none

    git clone https://github.com/astrophpeter/blast.git




