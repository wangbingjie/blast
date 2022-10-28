from django.test import TestCase
import api.validation as validation

class TestValidation(TestCase):

    def test_ra_validation(self):
        self.assertTrue(validation.ra_deg_valid(120.0) == True)
        self.assertTrue(validation.ra_deg_valid(-10.0) == False)
        self.assertTrue(validation.ra_deg_valid(123453420.0) == False)
        self.assertTrue(validation.ra_deg_valid("not a float") == False)

    def test_dec_validation(self):
        self.assertTrue(validation.dec_deg_valid(120.0) == False)
        self.assertTrue(validation.dec_deg_valid(-30.0) == True)
        self.assertTrue(validation.dec_deg_valid(123453420.0) == False)
        self.assertTrue(validation.dec_deg_valid("not a float") == False)
