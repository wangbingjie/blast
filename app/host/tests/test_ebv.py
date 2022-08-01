from django.test import TestCase

from ..transient_tasks import MWEBV_Transient, MWEBV_Host
from ..models import Transient
import numpy as np

class EBVTest(TestCase):
    fixtures = [
        "../fixtures/initial/setup_survey_data.yaml",
        "../fixtures/initial/setup_filter_data.yaml",
        "../fixtures/initial/setup_catalog_data.yaml",
        "../fixtures/initial/setup_status.yaml",
        "../fixtures/initial/setup_tasks.yaml",
        "../fixtures/initial/setup_acknowledgements.yaml",
        "../fixtures/example/2010h.yaml",
    ]

    def test_mwebv_transient(self):

        transient = Transient.objects.get(name='2010H')
        mwebv_cls = MWEBV_Transient()
        mwebv_cls._run_process(transient)
        
        assert(np.isclose(transient.milkyway_dust_reddening,0.0264890836,1e-5))

        mwebv_host_cls = MWEBV_Host()
        mwebv_host_cls._run_process(transient)
        
        assert(np.isclose(transient.host.milkyway_dust_reddening,0.026506094634532927,1e-5))
