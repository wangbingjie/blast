from django.test import TestCase

from ..models import TaskRegister
from ..models import Transient
from ..models import AperturePhotometry
from ..transient_tasks import ValidateGlobalPhotometry
from ..transient_tasks import ValidateLocalPhotometry


class TestValidatePhotometry(TestCase):
    fixtures = [
        "../fixtures/initial/setup_survey_data.yaml",
        "../fixtures/initial/setup_filter_data.yaml",
        "../fixtures/initial/setup_catalog_data.yaml",
        "../fixtures/initial/setup_status.yaml",
        "../fixtures/initial/setup_tasks.yaml",
        "../fixtures/initial/setup_acknowledgements.yaml",
        "../fixtures/test/test_2010h.yaml",
    ]

    def test_validate_local_photometry(self):

        transient = Transient.objects.get(name="2010H")
        vlp_cls = ValidateLocalPhotometry()

        status_message = vlp_cls._run_process(transient)

        # let's see which photometry is validated and which isn't
        validated_local_aperture_photometry = AperturePhotometry.objects.filter(
            transient=transient, aperture__type="local", is_validated=True
        )
        for v in validated_local_aperture_photometry:
            assert (
                "WISE_W2" not in v.filter.name
                and "WISE_W3" not in v.filter.name
                and "WISE_W4" not in v.filter.name
            )

        assert status_message == "processed"

    def test_validate_global_photometry(self):

        transient = Transient.objects.get(name="2010H")
        vgp_cls = ValidateGlobalPhotometry()

        status_message = vgp_cls._run_process(transient)

        not_validated_global_aperture_photometry = \
            AperturePhotometry.objects.filter(
            transient=transient, aperture__type="global", is_validated=False
        )

        assert len(not_validated_global_aperture_photometry) == 0
