from django.db import models
from astropy.coordinates import SkyCoord
from astropy import units as u

class SkyObject(models.Model):
    """
    Abstract base model to represent an astrophysical object.

    Attributes:
        name (django.db.model.CharField): Name of the sky object, character
            limit = 20.
        ra_deg (django.db.model.FloatField): Right Ascension (ICRS) in decimal
            degrees of the host
        deg_deg (django.db.model.FloatField): Declination (ICRS) in decimal degrees
            of the host
    """
    name = models.CharField(max_length=100, blank=True, null=True)
    ra_deg = models.FloatField()
    dec_deg = models.FloatField()

    class Meta:
        abstract = True

    @property
    def sky_coord(self):
        """
        SkyCoordinate of the object's position.
        """
        return SkyCoord(ra=self.ra_deg, dec=self.dec_deg, unit='deg')

    @property
    def ra(self):
        """
        String representation of Right ascension.
        """
        return self.sky_coord.ra.to_string(unit=u.hour, precision=2)

    @property
    def dec(self):
        """
        String representation of Declination.
        """
        return self.sky_coord.dec.to_string(precision=2)

class Host(SkyObject):
    """
    Model to represent a host galaxy.

    Attributes:
        name (django.db.model.CharField): Name of the host galaxy, character
            limit = 20.
        ra_deg (django.db.model.FloatField): Right Ascension (ICRS) in decimal
            degrees of the host
        deg_deg (django.db.model.FloatField): Declination (ICRS) in decimal degrees
            of the host
    """

class Transient(SkyObject):
    """
    Model to represent a transient.

    Attributes:
        tns_name (django.db.model.CharField): Transient Name
            Server name of the transient, character limit = 20.
        tns_id (models.IntegerField): Transient Name Server ID.
        tns_prefix (models.CharField): Transient Name Server name
            prefix, character limit = 20.
        ra_deg (django.db.model.FloatField): Right Ascension (ICRS) in decimal
            degrees of the transient.
        deg_deg (django.db.model.FloatField): Declination (ICRS) in decimal
            degrees of the transient.
        host (django.db.model.ForeignKey): ForeignKey pointing to a :class:Host
            representing a transient's host galaxy.
        public_timestamp (django.db.model.DateTimeField): Transient name server
            public timestamp for the transient. Field can be null or blank. On
            Delete is set to cascade.
        host_match_status (models.CharField): Processing host match status for
            house keeping on the blast web app, character limit = 20. Field can
            be null or blank.
        image_download_status (models.CharField): Processing image_download
            status for house keeping on the blast web app, character limit = 20.
            Field can be null or blank.
        catalog_photometry_status (models.CharField): Processing image_download
            status for house keeping on the blast web app, character limit = 20.
            Field can be null or blank.
    """
    tns_name = models.CharField(max_length=20)
    tns_id = models.IntegerField()
    tns_prefix = models.CharField(max_length=20)
    public_timestamp = models.DateTimeField(null=True, blank=True)
    host = models.ForeignKey(Host, on_delete=models.CASCADE, null=True, blank=True)
    host_match_status = models.CharField(max_length=20, default='not processed')
    image_download_status = models.CharField(max_length=20, default='not processed')
    catalog_photometry_status = models.CharField(max_length=20,default='not processed')

    def _status_badge_class(self, status):
        default_button_class = 'badge bg-secondary'
        warn_status = ['processing']
        bad_status = ['failed','no match' ]
        good_status = ['processed']

        if status in bad_status:
            badge_class = 'badge bg-danger'
        elif status in warn_status:
            badge_class = 'badge bg-warning'
        elif status in good_status:
            badge_class = 'badge bg-success'
        else:
            badge_class = default_button_class

        return badge_class

    @property
    def host_match_status_badge_class(self):
        return self._status_badge_class(self.host_match_status)

    @property
    def image_download_status_badge_class(self):
        return self._status_badge_class(self.image_download_status)

class Status(models.Model):
    """
    Status of a given processing task
    """
    message = models.CharField(max_length=20)
    type = models.CharField(max_length=20)

    @property
    def badge(self):
        """
        Returns the Boostrap badge class of the status
        """
        if self.type == 'error':
            badge_class = 'badge bg-danger'
        elif self.type == 'warning':
            badge_class = 'badge bg-warning'
        elif self.type == 'success':
            badge_class = 'badge bg-success'
        elif self.type == 'blank':
            badge_class = 'badge bg-secondary'
        else:
            badge_class = 'badge bg-secondary'

        return badge_class

class Task(models.Model):
    """
    A proceesing task that needs to be completed for a transient.
    """
    name = models.CharField(max_length=20)

class TransientProcessingStatus(models.Model):
    """
    Keep track of the the various processing status of a transient.
    """
    name = models.ForeignKey(Task, on_delete=models.CASCADE, null=True,
                             blank=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True,
                             blank=True)
    transient = models.ForeignKey(Transient, on_delete=models.CASCADE, null=True,
                             blank=True)

class ExternalResourceCall(models.Model):
    """
    A model to represent a call to a call to an external resource.

    Attributes:
        resource_name (models.CharField): Name of the external resource.
        response_status (models.CharField): Response status returned when the
            external resource was requested.
        request_time (models.DateTimeField): Time of request to the resource.
    """
    resource_name = models.CharField(max_length=20)
    response_status = models.CharField(max_length=20)
    request_time = models.DateTimeField(null=True, blank=True)

class SurveyManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Survey(models.Model):
    """
    Model to represent a survey
    """
    name = models.CharField(max_length=20, unique=True)
    objects = SurveyManager()


class FilterManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Filter(models.Model):
    """
    Model to represent a survey filter
    """
    name = models.CharField(max_length=20, unique=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    sedpy_id = models.CharField(max_length=20)
    hips_id = models.CharField(max_length=250)
    vosa_id = models.CharField(max_length=20)
    image_download_method = models.CharField(max_length=20)
    pixel_size_arcsec = models.FloatField()
    wavelength_eff_angstrom = models.FloatField()
    wavelength_min_angstrom = models.FloatField()
    wavelength_max_angstrom = models.FloatField()
    vega_zero_point_jansky = models.FloatField()

    objects = FilterManager()

    def __str__(self):
        return self.name


class CatalogManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Catalog(models.Model):
    """
    Model to represent a photometric catalog
    """
    name = models.CharField(max_length=100, unique=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    vizier_id = models.CharField(max_length=20)
    id_column = models.CharField(max_length=20)
    ra_column = models.CharField(max_length=20)
    dec_column = models.CharField(max_length=20)

    objects = CatalogManager()


class CatalogPhotometry(models.Model):
    name = models.CharField(max_length=100, unique=True)
    mag_column = models.CharField(max_length=20)
    mag_error_column = models.CharField(max_length=20)
    filter = models.ForeignKey(Filter, on_delete=models.CASCADE)
    catalog = models.ForeignKey(Catalog, on_delete=models.CASCADE)


def fits_file_path(instance, filename):
    """
    Constructs a file path for a fits image
    """
    return f'{instance.host}/{instance.filter.survey}/{instance.filter}.fits'



class Cutout(models.Model):
    """
    Model to represent a cutout image of a host galaxy
    """
    filter = models.ForeignKey(Filter, on_delete=models.CASCADE)
    transient = models.ForeignKey(Transient, on_delete=models.CASCADE, null=True, blank=True)
    fits = models.FileField(upload_to=fits_file_path, null=True, blank=True)



#class Image(models.Model):
#    """
#    Model to represent an image
#    """
#    host = models.ForeignKey(Host, on_delete=models.CASCADE)
#    filter = models.ForeignKey(Filter, on_delete=models.CASCADE)
#    file_path = models.CharField()




#class Match(models.Model):
#    """
#    Model to track the matches between and host and transient
#    """

#class HostApeturePhotometry(models.Model):
#    """
#    Model to represent forced apeture host photometry
#    """
#    pass


#class HostCatalogPhotometry(models.Model):
#    """
#    Model to represent catalog photometry of a known host
#    """
#    pass
































