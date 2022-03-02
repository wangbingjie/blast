from django.test import TestCase


class ViewTest(TestCase):
    fixtures = ["setup_test_transient.yaml"]

    def test_transient_list_page(self):
        response = self.client.get("/transients/")
        self.assertEqual(response.status_code, 200)

    def test_transient_page(self):
        response = self.client.get("/transients/2022testone/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/transients/2022testtwo/")
        self.assertEqual(response.status_code, 200)
