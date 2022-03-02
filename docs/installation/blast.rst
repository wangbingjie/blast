.. toctree::
   :maxdepth: 2

Running blast locally
+++++++++++++++++++++

There are several ways to install and run blast locally. You might want to
do this if you want to contribute to the development of blast, or if you don't
want to use the live web app. This pages walks you through how to install blast
and get it running on your machine in a couple of different ways.

Docker
======

The recommended option for installing and running blast locally is to
use docker. It so strongly recommended in fact, that I'm not going to write
documentation on how to install and run blast any other way.

Install the Docker desktop app
-------------------------------

The first step is to install the docker desktop application, which can be found
`here <https://docs.docker.com/get-docker/>`_ for mac, windows, and linux based
systems.

Run the blast app locally
-------------------------

Clone the bast repository.

.. code:: none

    git clone https://github.com/astrophpeter/blast.git

Once in the blast directory, start the docker container.

.. code:: none

    bash run_blast.sh

.. note::
    The web app container may fail a couple of times while it waits for the
    database to be setup. Do not worry, this is normal. The web app container
    will restart automatically until it successfully connects to the database.

Then go to `localhost:8000/ <https://0.0.0.0/transients>`_ in your web browser
and blast should be running.

.. warning::
    Stating the web app via the `run_blast.sh` script deletes your local copy of
    the database in `data/database/` and the app runs with an empty database.

To stop blast from running, open a new terminal window and run.

.. code:: none

    docker compose down

To run tests with the blast app, run

.. code:: none

    bash run_blast_tests.sh
