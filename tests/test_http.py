import pytest, time, mock
from lib.http import PartialFile, validator
from hamcrest import *


class TestPartialFile(object):

    def test_http_set_range_last_500(self):
        range_header = PartialFile.filter_list('-500')
        file_size = 408500018
        expected_value = [408499518, 408500017]
        resp = PartialFile.set_range(range_header[0], file_size)
        assert_that(resp, equal_to(expected_value))
        pass

    def test_filter(self):
        range_list = '100-500,400-600,300-900,1000-2000'
        expected_value = [(100,900),(1000,2000)]
        resp = PartialFile.filter_list(range_list)
        assert_that(resp, equal_to(expected_value))


        range_list = '-500'
        expected_value = [('', 500)]
        resp = PartialFile.filter_list(range_list)
        assert_that(resp, equal_to(expected_value))

        range_list = '0-499,501-1000'
        expected_value = [(0, 499), (501,1000)]
        resp = PartialFile.filter_list(range_list)
        assert_that(resp, equal_to(expected_value))
