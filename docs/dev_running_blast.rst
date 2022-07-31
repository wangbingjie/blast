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
`here <https://docs.docker.com/get-docker/>`_ for mac, windows, and linux. Make
sure you have Docker Compose version 1.28.0 or later.

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
a TNS api bot (see `<https://www.wis-tns.org/bots>`_).

Run the blast app
-----------------

Once in the top level blast directory, start the docker containers. This command
brings up the full blast stack,

.. code:: none

    bash run/blast.run.sh full_dev

If you are only interested in running the web server and database, which is
usually sufficient for front end web development, you can run:

.. code:: none

    bash run/blast.run.sh slim_dev

Then go to `https://0.0.0.0:8000/ <https://0.0.0.0:8000/>`_  in your web browser,
after all the containers have started, and blast should be running.

Running blast in these two modes means you can edit most code and you will see
the resulting live changes in the web interface.

.. warning::
    Stating the web app via the :code:`run/blast.run.sh` script deletes
    your local copy of the database in :code:`data/database/` and the app runs
    with an empty database.

To stop blast from running, open a new terminal window and run and from the root
blast directory run,

.. code:: none

    docker compose --project-name blast --env-file env/.env.dev down


.. warning::

    When you stop the blast container make sure all services are stopped. You can see which
    services are running in the docker desktop app and stop services manually there.

Testing the blast app
---------------------

To run tests with the blast app, while the full_dev or slim_dev containers are
up, in a separate terminal run

.. code:: none

    bash run/blast.test.up.sh

This allows you to run the tests without stopping the containers. If you would
like to run the tests from scratch, (when the blast app is not up) run,

.. code:: none

    bash run/blast.run.sh test
