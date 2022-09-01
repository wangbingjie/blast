import astropy
import dynesty
import fsps
import h5py
import numpy as np
import pandas as pd
import pylab as plt
import sedpy
from astropy.coordinates import SkyCoord
from astroquery.sdss import SDSS
from django.conf import settings
from django.db.models import Q
from django.test import TestCase
from numpy.testing import assert_array_equal
from sedpy.observate import Filter as SedpyFilter
from sedpy.observate import load_filters

from ..models import AperturePhotometry
from ..models import Filter
from ..models import Host
from ..models import SEDFittingResult
from ..models import Transient
from ..transient_tasks import GlobalHostSEDFitting
from ..transient_tasks import LocalHostSEDFitting


class FilterTest(TestCase):
    fixtures = [
        "../fixtures/initial/setup_survey_data.yaml",
        "../fixtures/initial/setup_filter_data.yaml",
    ]

    def test_filter_conversion(self):
        """
        Test blast filter is converted to sedpy filter
        """

        for filter in Filter.objects.all():
            # raw_data = pd.read_csv(f'{settings.TRANSMISSION_CURVES_ROOT}/{filter.name}.txt',
            #                  header=None, delim_whitespace=True)
            # raw_wavelength, raw_transmission = raw_data[0].values, raw_data[1].values
            sedpy_filter = filter.transmission_curve()
            self.assertTrue(sedpy_filter.nick == filter.name)
            self.assertTrue(isinstance(sedpy_filter, SedpyFilter))
            # assert_array_equal(sedpy_filter.wavelength, raw_wavelength)
            # assert_array_equal(sedpy_filter.transmission, raw_transmission)


class PropsectorBuildObsTest(TestCase):
    fixtures = [
        "../fixtures/initial/setup_survey_data.yaml",
        "../fixtures/initial/setup_filter_data.yaml",
    ]

    def test_build_obs(self):
        pass


class SEDFittingFullTest(TestCase):

    fixtures = [
        "../fixtures/initial/setup_survey_data.yaml",
        "../fixtures/initial/setup_filter_data.yaml",
        "../fixtures/initial/setup_catalog_data.yaml",
        "../fixtures/initial/setup_status.yaml",
        "../fixtures/initial/setup_tasks.yaml",
        "../fixtures/initial/setup_acknowledgements.yaml",
        "../fixtures/test/test_2010h.yaml",
    ]

    # def test_prospector_global(self):

    #    transient = Transient.objects.get(name="2010H")

    #    sed_cls = GlobalHostSEDFitting()
    #    status_message = sed_cls._run_process(transient, mode="test")

    #    pr = SEDFittingResult.objects.filter(
    #        Q(transient=transient)
    #        & Q(aperture__type="global")
    #        & Q(posterior__contains="/tmp")
    #    )
    #    self.assertTrue(len(pr) == 1)
    #    self.assertTrue(status_message == "processed")
    #    self.assertTrue(pr[0].log_ssfr_50 != None)

    # def test_prospector_local(self):
    #
    #    transient = Transient.objects.get(name="2010H")

    #    sed_cls = LocalHostSEDFitting()
    #    status_message = sed_cls._run_process(transient, mode="test")
    #    pr = SEDFittingResult.objects.filter(
    #        Q(transient=transient)
    #        & Q(aperture__type="local")
    #        & Q(posterior__contains="/tmp")
    #    )
    #    self.assertTrue(len(pr) == 1)
    #    self.assertTrue(status_message == "processed")
    #    self.assertTrue(pr[0].log_ssfr_50 != None)
