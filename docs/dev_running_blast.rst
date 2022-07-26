Running blast locally
=====================

If you want to develop on blast, for most things, you will have to run blast
locally to see the effect of your code changes. This pages walks you through
how to install blast and get it running on your machine.

Install the Docker desktop app
-------------------------------

The recommended option for installing and running blast locally is to
use docker. It is so strongly recommended in fact, that I'm not going to write
documentation on how to install and run blast any other way. The first step is to
install the docker desktop application, which can be found
`here <https://docs.docker.com/get-docker/>`_ for mac, windows, and linux.

Clone the blast repository
--------------------------

Clone the bast repository.

.. code:: none

    git clone https://github.com/astrophpeter/blast.git

Setup environment file
----------------------

Blast needs some environment variables to run. All of
these should be located in the :code:`env/.env.dev` file. This file is not in
source control, you need to create and populate this file yourself.
It should follow the same format as the :code:`env/.env.dev.example` file. If you
do not need to ingest real transient data from TNS the example :code:`.env.file`
file should be sufficient with the TNS variables left blank. While in the
:code:`env/` directory run:

.. code:: none

    cp .env.dev.example .env.dev

If you do need to ingest real TNS for development you will need the details of
a TNS api bot (see ).

Run the blast app
-----------------

Once in the top level blast directory, start the docker container.

.. code:: none

    bash run/blast.run.local.sh

Then go to `https://0.0.0.0/ <https://0.0.0.0/>`_  in your web browser,
after all the containers have started, and blast should be running.

.. warning::
    Stating the web app via the :code:`run/blast.run.local.sh` script deletes
    your local copy of the database in :code:`data/database/` and the app runs
    with an empty database.

To stop blast from running, open a new terminal window and run.

.. code:: none

    docker compose down

Testing the blast app
---------------------

To run tests with the blast app, run

.. code:: none

    bash run/blast.tests.local.sh
