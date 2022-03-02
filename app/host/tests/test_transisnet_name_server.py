from django.test import TestCase

from ..transient_name_server import build_tns_header
from ..transient_name_server import build_tns_url


class BuildTNSHeaderTest(TestCase):
    def setUp(self):
        self.tns_bot_id = 12345
        self.tns_bot_name = "test_bot"
        self.header = build_tns_header(self.tns_bot_id, self.tns_bot_name)

    def test_marker(self):
        marker = self.header["User-Agent"]
        true_marker = (
            f'tns_marker{{"tns_id": {self.tns_bot_id},'
            f'"type": "bot", "name": "{self.tns_bot_name}"}}'
        )
        self.assertEqual(marker, true_marker)

    def test_return_type_is_dict(self):
        self.assertIsInstance(self.header, dict)

    def test_return_contains_correct_key(self):
        user_agent = self.header.get("User-Agent")
        self.assertTrue(user_agent is not None)

    def test_return_dictionary_size(self):
        self.assertTrue(len(self.header) == 1)


class BuildTNSUrlTest(TestCase):
    def test_search_mode(self):
        url = build_tns_url("test", mode="search")
        self.assertEqual(url, "test/Search")

    def test_get_mode(self):
        url = build_tns_url("test", mode="get")
        self.assertEqual(url, "test/object")

    def test_invalid_mode(self):
        with self.assertRaises(ValueError):
            build_tns_url("test", mode="something_else")
        with self.assertRaises(ValueError):
            build_tns_url("test")
