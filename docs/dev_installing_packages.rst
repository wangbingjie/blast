Adding new dependencies
=======================

Blast and all it's associated services are run in `docker <https://www.docker.com/>`_
containers. This allows the application to be portable. You may be working on
some code that requires you to add a new python package. To add this
dependency, you have to do two things.

1. Add the package and version to the :code:`app/requirements.txt`. This allows docker
to `pip install <https://pip.pypa.io/en/stable/cli/pip_install/>`_ your new package.

2. Change the :code:`BLAST_IMAGE` variable in your :code:`env/.env.dev` to be
:code:`blast_base` instead of :code:`blast_latest`. This will force docker to
build and install your package.

.. note::

    Setting :code:`BLAST_IMAGE=blast_latest` in your :code:`env/env.dev` means
    the latest `blast docker image <https://github.com/astrophpeter/blast/pkgs/container/blast>`_
    is downloaded and used when running blast locally. This is faster than building
    the image from scratch everytime. :code:`BLAST_IMAGE=blast_base` forces the
    image to be built from scratch which is required when you have added a new
    dependency. Eventually, when a new dependency is accepted into main it
    will become part of the blast latest image.
