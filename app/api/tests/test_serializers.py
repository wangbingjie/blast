import api.serializers as serializers
from django.test import TestCase


class SerializerValidationTest(TestCase):
    def test_transient_name_validation(self):
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
        value = serial.validate_name("2010h")
        self.assertTrue(value == "2010h")

        with self.assertRaises(Exception):
            serial.validate_name(2010.0)

    def test_transient_ra_validation(self):
        serial = serializers.TransientSerializer()
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

    def test_transient_dec_validation(self):
        serial = serializers.TransientSerializer()
        value = serial.validate_dec_deg(60.0)
        self.assertTrue(value == 60.0)

        with self.assertRaises(Exception):
            serial.validate_dec_deg("120.0")

        with self.assertRaises(Exception):
            serial.validate_dec_deg(-10000.0)

        with self.assertRaises(Exception):
            serial.validate_dec_deg(370.0)

        with self.assertRaises(Exception):
            serial.validate_dec_deg(None)

    def test_full_validation(self):
        transient_data = {
            "name": "2010-01-16T00:00:00Z",
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
