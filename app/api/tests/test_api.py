import json

from django.test import TestCase
from rest_framework.test import APIClient


class APITest(TestCase):
    fixtures = ["../fixtures/test/test_transient_data.yaml"]

    def test_transient_get(self):
        client = APIClient()
        request = client.get("/api/transient/2022testone/?format=json")
        data = json.loads(request.content)

        self.assertTrue(data["local_aperture_2MASS_H_flux"] == 2183.8)
        self.assertTrue(data["local_aperture_2MASS_H_flux_error"] == 224.97)
        self.assertTrue(data["local_aperture_2MASS_H_magnitude"] == 0.0)
        self.assertTrue(data["local_aperture_2MASS_H_magnitude_error"] == 0.0)

        self.assertTrue(data["local_aperture_2MASS_J_flux"] == 1091.48)
        self.assertTrue(data["local_aperture_2MASS_J_flux_error"] == 130.38)
        self.assertTrue(data["local_aperture_2MASS_J_magnitude"] == 0.0)
        self.assertTrue(data["local_aperture_2MASS_J_magnitude_error"] == 0.0)

        self.assertTrue(data["global_aperture_2MASS_J_flux"] == 99.0)
        self.assertTrue(data["global_aperture_2MASS_J_flux_error"] == 99.0)
        self.assertTrue(data["global_aperture_2MASS_J_magnitude"] == 0.0)
        self.assertTrue(data["global_aperture_2MASS_J_magnitude_error"] == 0.0)

        self.assertTrue(data["global_aperture_2MASS_H_flux"] == 1.0)
        self.assertTrue(data["global_aperture_2MASS_H_flux_error"] == 1.0)
        self.assertTrue(data["global_aperture_2MASS_H_magnitude"] == 10.0)
        self.assertTrue(data["global_aperture_2MASS_H_magnitude_error"] == 0.2)

        self.assertTrue(data["local_aperture_ra_deg"] == 121.6015)
        self.assertTrue(data["local_aperture_dec_deg"] == 1.03586)
        self.assertTrue(data["local_aperture_semi_major_axis_arcsec"] == 1.0)
        self.assertTrue(data["local_aperture_semi_minor_axis_arcsec"] == 1.0)
        self.assertTrue(data["local_aperture_cutout"] is None)

        self.assertTrue(data["global_aperture_ra_deg"] == 11.6015)
        self.assertTrue(data["global_aperture_dec_deg"] == 10.03586)
        self.assertTrue(data["global_aperture_semi_major_axis_arcsec"] == 0.4)
        self.assertTrue(data["global_aperture_semi_minor_axis_arcsec"] == 0.5)
        self.assertTrue(data["global_aperture_cutout"] == "2MASS_J")

        self.assertTrue(data["transient_name"] == "2022testone")
        self.assertTrue(data["host_name"] == "PSO J080624.103+010209.859")

    def test_transient_post(self):
        client = APIClient()
