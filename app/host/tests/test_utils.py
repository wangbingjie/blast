from django.test import TestCase
from ..host_utils import survey_list
from ..cutouts import cutout
from astropy.coordinates import SkyCoord

class CutoutDownloadTest(TestCase):

    def setUp(self):
        self.surveys = survey_list('host/data/survey_metadata.yml')

    def test_cutout_download(self):
        """
        Test that cutout data can be downloaded.
        """
        for survey in self.surveys:
            position = SkyCoord(ra=survey.test_ra_deg,
                                dec=survey.test_dec_deg,
                                unit='deg')
            cutout_data = cutout(position, survey)
            with self.subTest(survey=survey.name):
                self.assertTrue(cutout_data != None)
