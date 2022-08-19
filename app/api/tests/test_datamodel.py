from django.test import TestCase
from host import models

from .. import serializers
from ..components import host_component
from ..components import transient_component
from ..datamodel import serialize_blast_science_data


class DatamodelConstructionTest(TestCase):
    fixtures = ["../fixtures/test/filters.yaml", "../fixtures/test/test_transient.yaml"]

    def test_datamodel_build(self):
        host = host_component("2022testone")
        transient = transient_component("2022testone")
        data = serialize_blast_science_data(host + transient)
        self.assertTrue(type(data) is dict)
