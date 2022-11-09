import api.serializers as serializers
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
        serial.is_valid()
        serial.save()

        transient = models.Transient.objects.get(name__exact="2010h")
        object_data = serializers.TransientSerializer(transient).data
        self.assertTrue(object_data == transient_data)


class TransientSerializerUpdateTest(TestCase):
    fixtures = ["../fixtures/test/test_transient_upload.yaml"]

    def test_transient_update(self):
        transient_data = {
            "name": "2022testone",
            "ra_deg": 121.6015,
            "dec_deg": 1.03586,
            "public_timestamp": "2010-01-16T00:00:00Z",
            "redshift": None,
            "milkyway_dust_reddening": None,
            "spectroscopic_class": "SN 1a",
            "photometric_class": None,
            "processing_status": "processing",
        }

        transient = models.Transient.objects.get(name__exact="2022testone")

        serial = serializers.TransientSerializer(transient, data=transient_data)
        serial.is_valid()
        serial.save()

        transient = models.Transient.objects.get(name__exact="2022testone")
        self.assertTrue(transient.ra_deg == 121.6015)
        self.assertTrue(transient.dec_deg == 1.03586)
        self.assertTrue(transient.tns_id == 9999)
        self.assertTrue(transient.tasks_initialized == "True")


class HostSerializerCreateTest(TestCase):
    fixtures = ["../fixtures/test/test_host_upload.yaml"]

    def test_host_create(self):
        host_data = {
            "name": "testhost",
            "ra_deg": 121.6015,
            "dec_deg": 1.03586,
            "redshift": 0.1,
            "photometric_redshift": 0.3,
            "milkyway_dust_reddening": 0.4,
        }

        transient = models.Transient.objects.get(name__exact="2022testone")
        serial = serializers.HostSerializer(data=host_data)
        serial.is_valid()
        serial.save(transient=transient)
        transient = models.Transient.objects.get(name__exact="2022testone")
        self.assertTrue(transient.host.name == "testhost")
        self.assertTrue(transient.host.ra_deg == 121.6015)
        self.assertTrue(transient.host.dec_deg == 1.03586)
        self.assertTrue(transient.host.redshift == 0.1)
        self.assertTrue(transient.host.milkyway_dust_reddening == 0.4)


class HostSerializerUpdateTest(TestCase):
    fixtures = ["../fixtures/test/test_host_update.yaml"]

    def test_host_update(self):
        host_data = {
            "name": "testhost",
            "ra_deg": 100.0,
            "dec_deg": 1.0,
            "redshift": 0.05,
            "photometric_redshift": 0.3,
            "milkyway_dust_reddening": 0.5,
        }

        transient = models.Transient.objects.get(name__exact="2022testone")
        self.assertTrue(transient.host.name == "PSO J080624.103+010209.859")
        host = models.Host.objects.get(transient=transient)
        serial = serializers.HostSerializer(host, data=host_data)
        serial.is_valid()
        serial.save(transient=transient)
        transient = models.Transient.objects.get(name__exact="2022testone")
        self.assertTrue(transient.host.name == "testhost")
        self.assertTrue(transient.host.ra_deg == 100.0)
        self.assertTrue(transient.host.dec_deg == 1.0)
        self.assertTrue(transient.host.redshift == 0.05)
        self.assertTrue(transient.host.milkyway_dust_reddening == 0.5)

class ApertureSerializerCreateTest(TestCase):
    fixtures = ["../fixtures/test/test_aperture_upload.yaml"]


    def test_aperture_create(self):

        aperture_data = {
            "ra_deg": 100.0,
            "dec_deg": -30.0,
            "orientation_deg": 10.0,
            "semi_major_axis_arcsec": 5.0,
            "semi_minor_axis_arcsec": 3.0,
            "cutout": "2MASS_J"
        }

        transient = models.Transient.objects.get(name__exact="2022testone")
        type = "local"
        serial = serializers.ApertureSerializer(data=aperture_data)
        serial.is_valid()
        serial.save(transient=transient, type=type)

        aperture = models.Aperture.objects.get(transient=transient)
        self.assertTrue(aperture.ra_deg == 100.0)
        self.assertTrue(aperture.dec_deg == -30.0)
        self.assertTrue(aperture.orientation_deg == 10.0)
        self.assertTrue(aperture.semi_major_axis_arcsec == 5.0)
        self.assertTrue(aperture.semi_minor_axis_arcsec == 3.0)
        self.assertTrue(aperture.name == "2022testone_local")
        self.assertTrue(aperture.transient.name == "2022testone")

class ApertureSerializerUpdateTest(TestCase):
    fixtures = ["../fixtures/test/test_aperture_update.yaml"]


    def test_aperture_update(self):

        aperture_data = {
            "ra_deg": 100.0,
            "dec_deg": -30.0,
            "orientation_deg": 10.0,
            "semi_major_axis_arcsec": 5.0,
            "semi_minor_axis_arcsec": 3.0,
            "cutout": "2MASS_J"
        }

        transient = models.Transient.objects.get(name__exact="2022testone")
        aperture = models.Aperture.objects.get(transient=transient)
        type = "local"
        serial = serializers.ApertureSerializer(aperture, data=aperture_data)
        serial.is_valid()
        serial.save(transient=transient, type=type)

        aperture = models.Aperture.objects.get(transient=transient)
        self.assertTrue(aperture.ra_deg == 100.0)
        self.assertTrue(aperture.dec_deg == -30.0)
        self.assertTrue(aperture.orientation_deg == 10.0)
        self.assertTrue(aperture.semi_major_axis_arcsec == 5.0)
        self.assertTrue(aperture.semi_minor_axis_arcsec == 3.0)
        self.assertTrue(aperture.name == "2022testone_local")
        self.assertTrue(aperture.transient.name == "2022testone")
