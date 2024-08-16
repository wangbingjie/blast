import numpy as np
from django.test import TestCase

from ..models import Transient
from ..transient_tasks import MWEBV_Host
from ..transient_tasks import MWEBV_Transient


class EBVTest(TestCase):

    def test_mwebv_transient(self):
        transient = Transient.objects.get(name="2010H")
        mwebv_cls = MWEBV_Transient(transient_name=transient.name)
        status_message = mwebv_cls._run_process(transient)

        assert np.isclose(transient.milkyway_dust_reddening, 0.0264890836, 1e-5)
        assert status_message == "processed"

        mwebv_host_cls = MWEBV_Host(transient_name=transient.name)
        status_message = mwebv_host_cls._run_process(transient)

        assert np.isclose(
            transient.host.milkyway_dust_reddening, 0.026506094634532927, 1e-5
        )
        assert status_message == "processed"

        # check the failure mode of a bad ra/dec
        transient.dec_deg = -99
        status_message = mwebv_cls._run_process(transient)
        assert status_message == "no transient MWEBV"

        transient.host.dec_deg = -99
        status_message = mwebv_host_cls._run_process(transient)
        assert status_message == "no host MWEBV"
