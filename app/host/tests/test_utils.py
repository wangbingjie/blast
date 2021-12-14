from django.test import TestCase
from ..host_utils import cutout, survey_list
from astropy.coordinates import SkyCoord

class CutoutDownloadTest(TestCase):

    def setUp(self):
        self.surveys = survey_list('host/data/survey_metadata.yml')[:7]

    def test_cutout_download(self):
        """
        Test that cutout data can be downloaded \n
        """
        for survey in self.surveys:
            position = SkyCoord(ra=survey.test_ra_deg,
                                dec=survey.test_dec_deg,
                                unit='deg')
            cutout_data = cutout(position, survey)
            with self.subTest(survey=survey.name):
                print(survey.name)
                self.assertTrue(cutout_data != None)
