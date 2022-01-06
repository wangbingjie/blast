from django.db import models


#class Transient(models.Model):
#    """
#    Model to represent a transient
#    """
#    name = models.CharField(max_length=20)
#    ra_deg = models.FloatField()
#    dec_deg = models.FloatField()


#class Host(models.Model):
#    """
#    Model to represent a Host Galaxy
#    """
#    name = models.CharField(max_length=20)
#    ra_deg = models.FloatField()
#    dec_deg = models.FloatField()


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


    objects = FilterManager()


#class Catalog(models.Model):
#    """
#    Model to represent a pre produced photometric catalog
#    """
#    name = models.CharField(max_length=20)
#    filter = models.ForeignKey(Filter, on_delete=models.CASCADE)
#    vizeir_id = models.CharField(max_length=20)


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
































