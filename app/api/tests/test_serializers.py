import api.serializers as serializers
from django.test import TestCase


class SerializerValidationTest(TestCase):
<<<<<<< HEAD
    def test_ra_validation(self):
        serializer_objs = [serializers.TransientSerializer(),
                       serializers.HostSerializer(),
                       serializers.ApertureSerializer()]

        for serializer in serializer_objs:
            serial = serializer
            value = serial.validate_ra_deg(120.0)
            self.assertTrue(value == 120.0)
=======
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
>>>>>>> 2b6fddd449e812785b0c42da961652a8a3a60b29

            with self.assertRaises(Exception):
                serial.validate_ra_deg("120.0")

            with self.assertRaises(Exception):
                serial.validate_ra_deg(-10000.0)

            with self.assertRaises(Exception):
                serial.validate_ra_deg(370.0)

            with self.assertRaises(Exception):
                serial.validate_ra_deg(None)

    def test_dec_validation(self):
        serializer_objs = [serializers.TransientSerializer(),
                           serializers.HostSerializer(),
                           serializers.ApertureSerializer()]

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

        transient_data_bad = {
            "name": 12342,
            "ra_deg": 121.6015,
            "dec_deg": 1.03586,
            "public_timestamp": 2010.1234,
            "redshift": None,
            "milkyway_dust_reddening": None,
            "spectroscopic_class": "SN 1a",
            "photometric_class": None,
            "processing_status": "processing"
        }
        serial = serializers.TransientSerializer(data=transient_data_bad)
        self.assertTrue(serial.is_valid() is False)
