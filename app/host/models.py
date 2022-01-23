from django.db import models


class Host(models.Model):
    """
    Model to represent a Host Galaxy

    Attributes:
        name (django.db.model.CharField(max_length=20)): name of the host galaxy
        ra_deg (django.db.model.FloatField): Right Ascension (ICRS) in decimal
            degrees of the host
        deg_deg (django.db.model.FloatField): Declination (ICRS) in decimal degrees
            of the host
    """
    name = models.CharField(max_length=20)

    ra_deg = models.FloatField()
    dec_deg = models.FloatField()

class Transient(models.Model):
    """
    Model to represent a transient

    Attributes:
        tns_name (django.db.model.CharField(max_length=20)): Transient Name
            Server name of the transient
        tns_id (models.CharField(max_length=20)): Transient Name Server ID
        tns_prefix (models.CharField(max_length=20)): Transient Name Server name
            prefix.
        ra_deg (django.db.model.FloatField): Right Ascension (ICRS) in decimal
            degrees of the transient
        deg_deg (django.db.model.FloatField): Declination (ICRS) in decimal degrees
            of the transient
        host (django.db.model.ForeignKey(Host, on_delete=models.CASCADE, null=True,blank=True):
            ForeignKey pointing to a :class:Host representing a transients host galaxy
        processing_status (models.CharField(max_length=20) : Current processing
            status on the blast web app
    """
    tns_name = models.CharField(max_length=20, blank=True, null=True)
    tns_id = models.CharField(max_length=20, blank=True, null=True)
    tns_prefix = models.CharField(max_length=20, blank=True, null=True)
    ra_deg = models.FloatField()
    dec_deg = models.FloatField()
    host = models.ForeignKey(Host,
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True)
    processing_status = models.CharField(max_length=20,
                                         default='not processed')

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
    hips_id = models.CharField(max_length=20)
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
    name = models.CharField(max_length=20, unique=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    vizier_id = models.CharField(max_length=20)
    id_column = models.CharField(max_length=20)
    ra_column = models.CharField(max_length=20)
    dec_column = models.CharField(max_length=20)

    objects = CatalogManager()


class CatalogPhotometry(models.Model):
    name = models.CharField(max_length=20, unique=True)
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
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
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
































