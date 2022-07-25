Repository overview
=========================

This section gives a high-level overview of the blast repository. It is
designed to help new developers navigate the code.

run
---

The :code:`run/` directory contains the scripts to start or test the blast
application either locally or on github actions.

nginx
-----

The :code:`run/` directory contains the nginx config file which controls how the
application is served.

docs
----

The :code:`docs/` directory contains all the code and text used to make the
documentation (which you are reading right now). If you are making a
documentation addition of change only, you will only edit code is this
directory.

docker
------

The :code:`docker/` directory contains the docker compose files used to start
all the services blast uses (e.g., database, web app, web server). It contains
docker compose files for running and testing the blast.

env
---

The :code:`env/` directory contains all the .env files which have all the blast
setting which we don't want to make visible in source control (e.g., database
login details).

data
----

The :code:`data/` directory contains all the data blast needs to operate. When
the application is running this is the default location where all data is stored
(e.g., database files and cutouts images). In source control, there is critical
data (transmission curves) and some example data (example cutout images) used
to populate offline local versions of blast during development.

.github
-------

The :code:`.github/` directory contains the files and templates used for feature
request and bug reports. It also contains workflows for continuous integration
testing.

app
---

The :code:`app/` directory contains all the blast django app source code. We
will provide a more detailed breakdown below.

entrypoints
+++++++++++













