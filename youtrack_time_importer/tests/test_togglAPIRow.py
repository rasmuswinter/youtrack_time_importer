from unittest import TestCase
from unittest.mock import MagicMock
from youtrack_time_importer.row import TogglAPIRow
from youtrack_time_importer.row import YoutrackMissingConnectionException
from youtrack_time_importer.row import YoutrackWorkItemIncorrectException
from youtrack_time_importer.row import YoutrackIssueNotFoundException
from youtrack import WorkItem
from youtrack import Issue
from youtrack import YouTrackException

__author__ = 'Matthew'

mockResponse = MagicMock(headers=list(), content=list(), code=404)


def attribute_error(issue_id, work_item):
    description = work_item.description
    duration = work_item.duration
    date = work_item.date


class TestTogglAPIRow(TestCase):
    def setUp(self):
        self.data = {
            'user': 'Mkendon',
            'tags': ['Youtracked'],
            'use_stop': True,
            'description': 'BCSM-15 Support new presences in code',
            'dur': 12294000,
            'billable': None,
            'pid': 6337533,
            'tid': None,
            'cur': None,
            'is_billable': False,
            'end': '2014-10-06T18:29:54+01:00',
            'updated': '2014-10-06T22:43:19+01:00',
            'start': '2014-10-06T15:05:00+01:00',
            'client': 'British Council',
            'task': None, 'project':
            'Social Monitor',
            'id': 166078570,
            'uid': 907967
        }
        connection = MagicMock()
        self.row = TogglAPIRow(self.data, connection)

    def test_work_item(self):
        work_item = self.row.work_item
        self.assertIsInstance(work_item, WorkItem)
        self.assertEqual('BCSM-15 Support new presences in code', work_item.description)
        self.assertEqual('205', work_item.duration)
        self.assertEqual('1412604300000', work_item.date)

    def test__str__(self):
        self.assertEqual(self.row.__str__(), "BCSM-15 Support new presences in code - 15:05 06/10/14")

    def test_is_ignored(self):
        self.assertFalse(self.row.is_ignored())

    def test_is_ignored_when_ignore_tag_is_present(self):
        self.row.data.get("tags").append("ignore")
        self.assertTrue(self.row.is_ignored())

    def test_issue_id(self):
        self.assertEqual('BCSM-15', self.row.issue_id)

    def test_issue_id_return_false_if_no_issue_id(self):
        self.row.data['description'] = "Support new presences in code"
        self.assertFalse(self.row.issue_id)

    def test_save_work_item_raises_exception_if_no_connection(self):
        self.row.connection = "connection"
        work_item = WorkItem()
        work_item.description = "Test Description"
        work_item.duration = "10"
        work_item.date = "1000"
        self.row.work_item = work_item
        self.assertRaises(YoutrackMissingConnectionException, self.row.save_work_item)

    def test_save_work_item_raise_exception_if_issue_doesnt_exist(self):
        self.row.connection.createWorkItem = MagicMock(side_effect=YouTrackException("", mockResponse))
        self.row.data['description'] = "Support new presences in code"
        work_item = WorkItem()
        work_item.description = "Test Description"
        work_item.duration = "10"
        work_item.date = "1000"
        self.row.work_item = work_item
        self.assertRaises(YoutrackIssueNotFoundException, self.row.save_work_item)

    def test_save_work_item_raise_exception_if_work_item_missing_description(self):
        self.row.connection.createWorkItem = MagicMock(side_effect=attribute_error)
        work_item = WorkItem()
        work_item.duration = "10"
        work_item.date = "1000"
        self.row.work_item = work_item
        self.assertRaises(YoutrackWorkItemIncorrectException, self.row.save_work_item)

    def test_save_work_item_raise_exception_if_work_item_missing_duration(self):
        self.row.connection.createWorkItem = MagicMock(side_effect=attribute_error)
        work_item = WorkItem()
        work_item.description = "Support new presences in code"
        work_item.date = "1000"
        self.row.work_item = work_item
        self.assertRaises(YoutrackWorkItemIncorrectException, self.row.save_work_item)

    def test_save_work_item_raise_exception_if_work_item_missing_date(self):
        self.row.connection.createWorkItem = MagicMock(side_effect=attribute_error)
        work_item = WorkItem()
        work_item.duration = "10"
        work_item.description = "Support new presences in code"
        self.row.work_item = work_item
        self.assertRaises(YoutrackWorkItemIncorrectException, self.row.save_work_item)
