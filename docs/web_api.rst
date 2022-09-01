Web API
=======

Blast also provides an application programming interface, which you can use
to fetch blast data programmatically.

Downloading blast data via python
---------------------------------

The url endpoint to grab the data for a particular transient is
:code:`/api/transient/get/<transient name>?format=json`.
Here is an example python snippet to load data as a python dictionary for the transient
2010h

.. code:: python

    from urllib.request import urlopen
    import json

    response = urlopen('<base_blast_url>/api/transient/2010h?format=json')
    data = json.loads(response.read())

Here data is a python dictionary that contains the blast science payload data m
model. We describe this model below.

Science payload data model
--------------------------

The data model for a single transient contains the following components.

Transient fields
++++++++++++++++

* :code:`transient_name` - name of the transient e.g., 2022abc
* :code:`transient_ra_deg` - transient Right Ascension in decimal degrees e.g., 132.34564
* :code:`transient_dec_deg` - transient declination in decimal degrees e.g., 60.123424
* :code:`transient_redshift` - transient redshift e.g., 0.01
* :code:`transient_milkyway_dust_reddening` - transient E(B-V) e.g, 0.2
* :code:`transient_processing_status` - blast processing status of the transient.
    "processed" - transient has been complement processed by blast and all data
    should be present in the science payload. "processing" - blast is still
    processing this transient and some parts of the science payload may not
    be populated at the current time. "blocked" - this transient has not been
    successfully fully processed by blast and some parts of the science payload
    will not be populated.

Host fields
+++++++++++

* :code:`host_name` - name of the host e.g., NGC123
* :code:`host_ra_deg` - host Right Ascension in decimal degrees e.g., 132.34564
* :code:`host_dec_deg` - host declination in decimal degrees e.g., 60.123424
* :code:`host_redshift` - transient redshift e.g., 0.01
* :code:`host_milkyway_dust_reddening` - host E(B-V) e.g, 0.2

Aperture fields
+++++++++++++++

<aperture_type> can either be "local" or "global".

* :code:`<aperture_type>_aperture_ra_deg` - aperture Right Ascension in decimal degrees e.g., 132.3456
* :code:`<aperture_type>_aperture_dec_deg` - aperture declination in decimal degrees e.g., 60.123424
* :code:`<aperture_type>_orientation_deg` - orientation angle of the aperture in decimal degrees e.g., 30.123
* :code:`<aperture_type>_semi_major_axis_arcsec` - semi major axis of the aperture in arcseconds
* :code:`<aperture_type>_semi_minor_axis_arcsec` - semi minor axis of the aperture in arcseconds
* :code:`<aperture_type>_cutout` - name of the cutout used to create aperture e.g, 2MASS_H, None if not cutout was used

Photometry fields
+++++++++++++++++

<aperture_type> can either be "local" or "global". <filter> can be any of the
filters blast downloads cutouts for e.g., 2MASS_H, 2MASS_J, SDSS_g ... . If the
data for a particular filter and transient does not exist the values will be None.

* :code:`<aperture_type>_aperture_<filter>_flux` - Aperture photometry flux in mJy
* :code:`<aperture_type>_aperture_<filter>_flux_error` - Aperture photometry flux error in mJy
* :code:`<aperture_type>_aperture_<filter>_magnitude` - Aperture photometry magnitude
* :code:`<aperture_type>_aperture_<filter>_magnitude_error` - Aperture photometry magnitude error

SED fit fields
++++++++++++++

<aperture_type> can either be "local" or "global". <parameter> can be either,

* "log_mass" (log base 10 of the host stellar mass [solar masses])
* "log_sfr" (log base 10 of the host star formation rate [solar masses / year])
* "log_ssfr" (log base 10 of the host specific star formation rate [/ year])
* "log_age" (log base 10 of the host stellar age [year])
* "log_tau" (log base 10 of the host star formation rate decline exponent [year])

<posterior_percentile> is the percentile value from the posterior distribution
which can either be "16", "50" ot "84"

* :code:`<aperture_type>_aperture_host_<parameter>_<posterior_percentile>`