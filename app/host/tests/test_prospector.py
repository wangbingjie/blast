import pandas as pd
from django.conf import settings
from django.test import TestCase
from ..models import Transient, Host, ProspectorResult, AperturePhotometry
from numpy.testing import assert_array_equal
from sedpy.observate import Filter as SedpyFilter

from ..models import Filter

import fsps
import dynesty
import sedpy
import h5py, astropy
import numpy as np
from scipy.special import gamma, gammainc

from astroquery.sdss import SDSS
from astropy.coordinates import SkyCoord
from sedpy.observate import load_filters
from prospect.utils.obsutils import fix_obs
from prospect.models.templates import TemplateLibrary
from prospect.models import SpecModel
from prospect.sources import CSPSpecBasis
from prospect.fitting import lnprobfn, fit_model
from prospect.io import write_results as writer
import prospect.io.read_results as reader

from ..prospector import build_obs,build_model
from ..transient_tasks import GlobalHostSEDFitting

import pylab as plt

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

class ProspectorFullTest(TestCase):

    fixtures = [
        "../fixtures/initial/setup_survey_data.yaml",
        "../fixtures/initial/setup_filter_data.yaml",
        "../fixtures/initial/setup_catalog_data.yaml",
        "../fixtures/initial/setup_status.yaml",
        "../fixtures/initial/setup_tasks.yaml",
        "../fixtures/initial/setup_acknowledgements.yaml",
        "../fixtures/test/test_2010h.yaml"
    ]

    def test_prospector(self):

        transient = Transient.objects.get(name="2010H")
        sed_cls = GlobalHostSEDFitting()
        status_message = sed_cls._run_process(transient,fast_mode=True)

        pr = ProspectorResult.objects.get(host=transient.host)
        self.assertTrue(status_message == 'processed')
        self.assertTrue(pr.log_ssfr_50 != None)
