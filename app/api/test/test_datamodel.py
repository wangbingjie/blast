from django.test import TestCase
from ..datamodel import DataModelComponent
from ..datamode import serialize_blast_science_data
from host import models
from .. import serializers

class DatamodelConstructionTest(TestCase):
    fixtures = ['../fixtures/test/filters.yaml',
                '../fixtures/test/test_transient.yaml']

    def test_datamodel_build(self):
        first_component = DataModelComponent(
            prefix="host_",
            query={"transient__name__exact": "2022fp"},
            model=models.Host,
            serializer=serializers.HostSerializer,
        )

        second_component = DataModelComponent(
            prefix="transient_",
            query={"transient__name__exact": "2022yo"},
            model=models.Host,
            serializer=serializers.HostSerializer,
        )

        data = serialize_blast_science_data(first_component+second_component)
        self.assertTrue(1==2)


