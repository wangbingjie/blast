import itertools
from typing import List

from django.test import TestCase
from host import models

from .. import serializers
from ..components import data_model_components
from ..components import host_component
from ..components import transient_component
from ..datamodel import DataModelComponent
from ..datamodel import serialize_blast_science_data
from ..datamodel import unpack_component_groups


class DatamodelConstructionTest(TestCase):
    fixtures = ["../fixtures/test/test_transient_data.yaml"]

    def test_datamodel_build_with_data(self):
        host = host_component("2022testone")
        transient = transient_component("2022testone")
        data = serialize_blast_science_data(host + transient)
        self.assertTrue(data["transient_name"] == "2022testone")
        self.assertTrue(data["host_name"] == "PSO J080624.103+010209.859")

    def test_datamodel_build_without_data(self):
        host = host_component("thisTransientDoesNotExist")
        transient = transient_component("thisTransientDoesNotExist")
        data = serialize_blast_science_data(host + transient)
        self.assertTrue(data["transient_name"] is None)
        self.assertTrue(data["host_name"] is None)


class DataModelComponentTests(TestCase):
    def test_all_datamodel_components_output_type(self):
        for component in data_model_components:
            output = component("thisTransientDoesNotExist")
            self.assertIsInstance(output, List)
            for model_component in output:
                self.assertIsInstance(model_component, DataModelComponent)


class GroupComponentUnpackTest(TestCase):
    def test_component_group_unpacking(self):
        nested = [[1], [2], [3, 4]]
        nested_two = [[1], [2], [3], [4]]
        flat = [1, 2, 3, 4]
        unpack_nested = unpack_component_groups(nested)
        self.assertTrue(flat == unpack_nested)
        unpack_flat = unpack_component_groups(nested_two)
        self.assertTrue(flat == unpack_flat)
