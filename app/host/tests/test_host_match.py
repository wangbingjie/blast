from django.test import TestCase

from ..models import Transient
from ..transient_tasks import Ghost


class TestHostMatch(TestCase):

    def test_aperture_construction(self):
        transient = Transient.objects.get(name="2010H")

        host_cls = Ghost(transient_name=transient.name)

        status_message = host_cls._run_process(transient)

        assert status_message == "processed"
