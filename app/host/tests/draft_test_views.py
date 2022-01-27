from django.test import TestCase

class SubmitTransientViewTest(TestCase):

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/host/')
        self.assertEqual(response.status_code, 200)
