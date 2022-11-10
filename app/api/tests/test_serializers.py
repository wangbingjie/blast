import api.serializers as serializers
import api.components as components

from django.test import TestCase
from host import models


class SerializerValidationTest(TestCase):
    def test_ra_validation(self):
        serializer_objs = [
            serializers.TransientSerializer(),
            serializers.HostSerializer(),
            serializers.ApertureSerializer(),
        ]

        for serializer in serializer_objs:
            serial = serializer
            value = serial.validate_ra_deg(120.0)
            self.assertTrue(value == 120.0)

            with self.assertRaises(Exception):
                serial.validate_ra_deg("120.0")

            with self.assertRaises(Exception):
                serial.validate_ra_deg(-10000.0)

            with self.assertRaises(Exception):
                serial.validate_ra_deg(370.0)

            with self.assertRaises(Exception):
                serial.validate_ra_deg(None)

    def test_dec_validation(self):
        serializer_objs = [
            serializers.TransientSerializer(),
            serializers.HostSerializer(),
            serializers.ApertureSerializer(),
        ]

        for serializer in serializer_objs:
            serial = serializer
            value = serial.validate_dec_deg(-30.0)
            self.assertTrue(value == -30.0)

            with self.assertRaises(Exception):
                serial.validate_dec_deg("120.0")

            with self.assertRaises(Exception):
                serial.validate_dec_deg(-10000.0)

            with self.assertRaises(Exception):
                serial.validate_dec_deg(370.0)

            with self.assertRaises(Exception):
                serial.validate_dec_deg(None)

    def test_full_transient_validation(self):
        transient_data = {
            "name": "2010h",
            "ra_deg": 121.6015,
            "dec_deg": 1.03586,
            "public_timestamp": "2010-01-16T00:00:00Z",
            "redshift": None,
            "milkyway_dust_reddening": None,
            "spectroscopic_class": "SN 1a",
            "photometric_class": None,
            "processing_status": "processing",
        }
        serial = serializers.TransientSerializer(data=transient_data)
        self.assertTrue(serial.is_valid())

        transient_data_bad = {
            "name": "2010-01-16T00:00:00Z",
            "ra_deg": 121.6015,
            "dec_deg": 1.03586,
            "public_timestamp": 2010.1234,
            "redshift": None,
            "milkyway_dust_reddening": None,
            "spectroscopic_class": "SN 1a",
            "photometric_class": None,
            "processing_status": "processing",
        }
        serial = serializers.TransientSerializer(data=transient_data_bad)
        self.assertTrue(serial.is_valid() is False)

        transient_data_bad = {
            "name": 12342,
            "ra_deg": 121.6015,
            "dec_deg": 1.03586,
            "public_timestamp": 2010.1234,
            "redshift": None,
            "milkyway_dust_reddening": None,
            "spectroscopic_class": "SN 1a",
            "photometric_class": None,
            "processing_status": "processing",
        }
        serial = serializers.TransientSerializer(data=transient_data_bad)
        self.assertTrue(serial.is_valid() is False)


class SerializerCreateTest(TestCase):
    def test_transient_create(self):
        transient_data = {
            "transient_name": "2010h",
            "transient_ra_deg": 121.6015,
            "transient_dec_deg": 1.03586,
            "transient_public_timestamp": "2010-01-16T00:00:00Z",
            "transient_redshift": None,
            "transient_milkyway_dust_reddening": None,
            "transient_spectroscopic_class": "SN 1a",
            "transient_photometric_class": None,
            "transient_processing_status": "processing",
        }
        serial = serializers.TransientSerializer()
        data_model_component = components.transient_component("2010h")[0]
        serial.save(transient_data, data_model_component)

        transient = models.Transient.objects.get(name__exact="2010h")
        object_data = serializers.TransientSerializer(transient).data
        object_data = {f"transient_{key}": value for key, value in object_data.items()}
        self.assertTrue(object_data == transient_data)


class HostSerializerCreateTest(TestCase):
    fixtures = ["../fixtures/test/test_host_upload.yaml"]

    def test_host_create(self):
        host_data = {
            "transient_name": "2022testone",
            "host_name": "testhost",
            "host_ra_deg": 121.6015,
            "host_dec_deg": 1.03586,
            "host_redshift": 0.1,
            "host_photometric_redshift": 0.3,
            "host_milkyway_dust_reddening": 0.4,
        }

        serial = serializers.HostSerializer()
        data_model_component = components.host_component("2022testone")[0]
        serial.save(host_data, data_model_component)

        transient = models.Transient.objects.get(name__exact="2022testone")
        self.assertTrue(transient.host.name == "testhost")
        self.assertTrue(transient.host.ra_deg == 121.6015)
        self.assertTrue(transient.host.dec_deg == 1.03586)
        self.assertTrue(transient.host.redshift == 0.1)
        self.assertTrue(transient.host.milkyway_dust_reddening == 0.4)


class ApertureLocalSerializerCreateTest(TestCase):
    fixtures = ["../fixtures/test/test_aperture_upload.yaml"]

    def test_local_aperture_create(self):

        aperture_data = {
            "transient_name": "2022testone",
            "aperture_local_ra_deg": 100.0,
            "aperture_local_dec_deg": -30.0,
            "aperture_local_orientation_deg": 10.0,
            "aperture_local_semi_major_axis_arcsec": 5.0,
            "aperture_local_semi_minor_axis_arcsec": 3.0,
            "aperture_local_cutout": "2MASS_J",
        }

        serial = serializers.ApertureSerializer()
        data_model_component = components.aperture_component("2022testone")[0]
        serial.save(aperture_data, data_model_component)

        aperture = models.Aperture.objects.get(transient__name__exact="2022testone")
        self.assertTrue(aperture.ra_deg == 100.0)
        self.assertTrue(aperture.dec_deg == -30.0)
        self.assertTrue(aperture.orientation_deg == 10.0)
        self.assertTrue(aperture.semi_major_axis_arcsec == 5.0)
        self.assertTrue(aperture.semi_minor_axis_arcsec == 3.0)
        self.assertTrue(aperture.name == "2022testone_local")
        self.assertTrue(aperture.transient.name == "2022testone")

class ApertureGlobalSerializerCreateTest(TestCase):
    fixtures = ["../fixtures/test/test_aperture_upload.yaml"]

    def test_global_aperture_create(self):
        aperture_data = {
            "transient_name": "2022testone",
            "aperture_global_ra_deg": 100.0,
            "aperture_global_dec_deg": -30.0,
            "aperture_global_orientation_deg": 10.0,
            "aperture_global_semi_major_axis_arcsec": 5.0,
            "aperture_global_semi_minor_axis_arcsec": 3.0,
            "aperture_global_cutout": "2MASS_J",
        }

        serial = serializers.ApertureSerializer()
        data_model_component = components.aperture_component("2022testone")[1]
        serial.save(aperture_data, data_model_component)

        aperture = models.Aperture.objects.get(transient__name__exact="2022testone")
        self.assertTrue(aperture.ra_deg == 100.0)
        self.assertTrue(aperture.dec_deg == -30.0)
        self.assertTrue(aperture.orientation_deg == 10.0)
        self.assertTrue(aperture.semi_major_axis_arcsec == 5.0)
        self.assertTrue(aperture.semi_minor_axis_arcsec == 3.0)
        self.assertTrue(aperture.name == "2022testone_global")
        self.assertTrue(aperture.transient.name == "2022testone")
