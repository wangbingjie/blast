from django.test import TestCase

from ..models import Aperture
from ..models import TaskRegister
from ..models import Transient
from ..models import Status
from ..transient_tasks import Ghost

class TestHostMatch(TestCase):

    fixtures = [
        "../fixtures/initial/setup_survey_data.yaml",
        "../fixtures/initial/setup_filter_data.yaml",
        "../fixtures/initial/setup_catalog_data.yaml",
        "../fixtures/initial/setup_status.yaml",
        "../fixtures/initial/setup_tasks.yaml",
        "../fixtures/initial/setup_acknowledgements.yaml",
        "../fixtures/test/test_2010h.yaml",
    ]

    def test_aperture_construction(self):
        transient = Transient.objects.get(name="2010H")
        
        host_cls = Ghost()

        status_message = host_cls._run_process(transient)

        assert status_message == 'processed'
