Web API
=======



Downloading blast data
----------------------

The url endpoint to grab the data for a particular transient is
:code:`/api/transient/<transient name>?format=json`.
Here is am example python snippet to load data as a python dictionary for the transient
2010h

.. code:: python

    from urllib.request import urlopen
    import json

    response = urlopen('<base_blast_url>/api/transient/2010h?format=json')
    data = json.loads(response.read())
