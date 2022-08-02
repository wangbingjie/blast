import numpy as np
from django.test import TestCase

from ..models import TaskRegister
from ..models import Transient
from ..transient_tasks import MWEBV_Host
from ..transient_tasks import MWEBV_Transient


class EBVTest(TestCase):
    fixtures = [
        "../fixtures/initial/setup_survey_data.yaml",
        "../fixtures/initial/setup_filter_data.yaml",
        "../fixtures/initial/setup_catalog_data.yaml",
        "../fixtures/initial/setup_status.yaml",
        "../fixtures/initial/setup_tasks.yaml",
        "../fixtures/initial/setup_acknowledgements.yaml",
        "../fixtures/test/test_2010h.yaml",
    ]

    def test_mwebv_transient(self):

        transient = Transient.objects.get(name="2010H")
        mwebv_cls = MWEBV_Transient()
        status_message = mwebv_cls._run_process(transient)

        assert np.isclose(transient.milkyway_dust_reddening, 0.0264890836, 1e-5)
        assert status_message == "processed"

        mwebv_host_cls = MWEBV_Host()
        status_message = mwebv_host_cls._run_process(transient)

        assert np.isclose(
            transient.host.milkyway_dust_reddening, 0.026506094634532927, 1e-5
        )
        assert status_message == "processed"

        # check the failure mode of a bad ra/dec
        transient.dec_deg = -99
        status_message = mwebv_cls._run_process(transient)
        assert status_message == "not processed"

        transient.host.dec_deg = -99
        status_message = mwebv_host_cls._run_process(transient)
        assert status_message == "not processed"
