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

You can find image_ID in the Docker Desktop app or by running

.. code:: none

    docker images

Then go to `localhost:8000/<localhost:8000/>`_ in your web browser
and blast should be running.

Native install
==============

The other option to install blast is a native install. The recommended way to do
this is to create an isolated python environment and then install all the required
packages within that environment.

Install the Django app with Conda
---------------------------------

.. code:: none

    git clone https://github.com/astrophpeter/blast.git

Create a conda environment called blast using the ``blast/environment.yml`` file.
Assuming that you are in the top level blast directory:

.. code:: none

    conda env create -f environment.yml

Activate the conda environment and then pip install all required packages
using the ``blast/app/requirements.txt`` file

.. code:: none

    conda activate blast

Install pip in the environment

.. code:: none

    conda install pip

Locate the pip for the conda environment by running

.. code:: none

    which -a pip

which will produce a few paths, find the path with ``blast/`` in it and pip
install the rest of the requirements

.. code:: none

    your_pip_path install -r app/requirements.txt

Set up the transient name server bot
------------------------------------

For blast to ingest live data from the
`transient name server (TNS) <https://www.wis-tns.org/>`_ you need to
credentials for a TNS bot. To set up a TNS bot go
`here <https://www.wis-tns.org/user/register>`_ and create a TNS user account.
To avoid exposing these credentials blast looks for them in your environment.
Specifically, in your environment you need the following variables set:

.. code:: none

    export TNS_BOT_API_KEY=your_api_key
    export TNS_BOT_ID=your_bot_id
    export TNS_BOT_USERNAME=your_bot_user_name


Populate the database
---------------------

In order for blast to run you need to populate the backend databases with meta
information about surveys and external services blast uses. To do this run the
commands in the ``blast/app/populate_database_commands..txt``

.. code:: none

    bash populate_database_commands.txt





