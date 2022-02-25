from django.test import TestCase
from ..processing import TaskRunner


class TaskRunnerTest(TestCase):
    fixtures = ['setup_test_transient.yaml',
                'setup_tasks.yaml',
                'setup_status.yaml']

    def test_test(self):
        self.assertEqual(1,1)

