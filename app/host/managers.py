"""
Defines the natural keys for model objects to be de-serialized with.
"""
from django.db import models

class ExternalRequestManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)
    

class TransientManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class StatusManager(models.Manager):
    def get_by_natural_key(self, message):
        return self.get(message=message)


class TaskManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class SurveyManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class CatalogManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class FilterManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class HostManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class CutoutManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class ApertureManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)
