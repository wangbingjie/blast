from django.test import TestCase


class ViewTest(TestCase):
    fixtures = ["../fixtures/test/setup_test_transient.yaml"]

    def test_transient_list_page(self):
        response = self.client.get("/transients/")
        self.assertEqual(response.status_code, 200)

    def test_transient_page(self):
        response = self.client.get("/transients/2022testone/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/transients/2022testtwo/")
        self.assertEqual(response.status_code, 200)


class SEDPlotTest(TestCase):
    fixtures = [
        "../fixtures/initial/setup_survey_data.yaml",
        "../fixtures/initial/setup_filter_data.yaml",
        "../fixtures/initial/setup_catalog_data.yaml",
        "../fixtures/initial/setup_status.yaml",
        "../fixtures/initial/setup_tasks.yaml",
        "../fixtures/initial/setup_acknowledgements.yaml",
        "../fixtures/test/test_2010H.yaml",
    ]

    def test_tansient_page(self):
        response = self.client.get("/transients/2010H/")
        self.assertEqual(response.status_code, 200)
