from django.test import TestCase
from host import models

from .. import serializers
from ..datamodel import serialize_blast_science_data
from ..components import host_component
from ..components import transient_component

class DatamodelConstructionTest(TestCase):
    fixtures = ["../fixtures/test/filters.yaml", "../fixtures/test/test_transient.yaml"]

    def test_datamodel_build_with_data(self):
        host = host_component("2022testone")
        transient = transient_component("2022testone")
        data = serialize_blast_science_data(host+transient)
        self.assertTrue(data["transient_name"] == "2022testone")
        self.assertTrue(data["host_name"] == "PSO J080624.103+010209.859")

    def test_datamodel_build_without_data(self):
        host = host_component("thisTransientDoesNotExist")
        transient = transient_component("thisTransientDoesNotExist")
        data = serialize_blast_science_data(host+transient)
        self.assertTrue(data["transient_name"] is None)
        self.assertTrue(data["host_name"] is None)


