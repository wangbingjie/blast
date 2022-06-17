import os

from astropy.coordinates import SkyCoord
from astropy.io import fits
from django.test import TestCase

from ..cutouts import cutout
from ..models import Filter

sn = ["2010ag", "2010ai", "2010y", "2010h", ""]


class CutoutDownloadTest(TestCase):
    fixtures = [
        "../fixtures/initial/setup_survey_data.yaml",
        "../fixtures/initial/setup_filter_data.yaml",
    ]

    def setUp(self):
        self.transient_name = "2010ag"
        self.transient_ra = 355.53628555
        self.transient_dec = 48.70907059166666

    def test_cutout_download(self):
        """ "
        Test that cutout data can be downloaded.
        """
        # for filter in Filter.objects.all():
        #    position = SkyCoord(
        #        ra=self.transient_ra, dec=self.transient_dec, unit="deg")
        #    cutout_data = cutout(position, filter)
        #
        #    if cutout_data:
        #        save_dir = f"{self.transient_name}/{filter.name}/"
        #        os.makedirs(save_dir, exist_ok=True)
        #        path_to_fits = save_dir + f"{filter.name}.fits"
        #        fits.writeto(path_to_fits, overwrite=True)

        # self.assertTrue(1==1)
