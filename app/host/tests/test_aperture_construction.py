from django.test import TestCase

from ..models import Aperture
from ..models import TaskRegister
from ..models import Transient
from ..models import Status
from ..transient_tasks import GlobalApertureConstruction

class TestApertureConstruction(TestCase):

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
        
        gac_cls = GlobalApertureConstruction()

        status_message = gac_cls._run_process(transient)

        assert status_message == 'processed'

