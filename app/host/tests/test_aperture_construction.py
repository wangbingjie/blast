import numpy as np
from astropy.io import fits
from django.test import TestCase

from ..host_utils import build_source_catalog
from ..host_utils import estimate_background
from ..models import Aperture
from ..models import Status
from ..models import TaskRegister
from ..models import Transient
from ..transient_tasks import GlobalApertureConstruction


class TestApertureConstruction(TestCase):

    fixtures = [
        "../fixtures/initial/setup_survey_data.yaml",
        "../fixtures/initial/setup_filter_data.yaml",
        "../fixtures/initial/setup_catalog_data.yaml",
        "../fixtures/initial/setup_status.yaml",
        "../fixtures/initial/setup_tasks.yaml",
        "../fixtures/initial/setup_acknowledgements.yaml",
        "../fixtures/test/test_2010H.yaml",
    ]

    def test_aperture_construction(self):
        transient = Transient.objects.get(name="2010H")

        gac_cls = GlobalApertureConstruction()

        status_message = gac_cls._run_process(transient)

        assert status_message == "processed"

    def test_aperture_failures(self):

        data = np.zeros((500, 5000), dtype=np.float64)
        hdu = fits.PrimaryHDU(data=data)
        hdulist = fits.HDUList(hdus=[hdu])

        background = estimate_background(hdulist)
        catalog = build_source_catalog(hdulist, background)

        assert catalog is None
