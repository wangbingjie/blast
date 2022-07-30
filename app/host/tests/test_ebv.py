from django.test import TestCase

#from ..transient_tasks import MWEBV_Transient, MWEBV_Host
from ..models import Transient

class EBVTest(TestCase):
    fixtures = [
        "../fixtures/initial/setup_survey_data.yaml",
        "../fixtures/initial/setup_filter_data.yaml",
        "../fixtures/example/2010h.yaml",
    ]

    def test_mwebv_transient(self):

        pass
        
        #transient = Transient.objects.get(name='2010H')
        #mwebv_cls = MWEBV_Transient()
        #mwebv_cls._run_process(transient)

        #import pdb; pdb.set_trace()
