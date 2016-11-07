import pytest, time
from hamcrest import *
from lib.stats import Stats

@pytest.fixture(scope='module')
def get_psutil_process(request):
    import psutil, os
    return psutil.Process(os.getpid())

    
@pytest.fixture()
def get_stats_object(request, get_psutil_process):
    return Stats(get_psutil_process)


class TestStats(object):

    def test_add_bytes(self, get_stats_object):

        assert get_stats_object.get_bytes_streamed() == 0
        get_stats_object.add_bytes(5)
        assert get_stats_object.get_bytes_streamed() == 5

    def test_get_process_uptime_seconds(self, get_stats_object):
        #make sure the time keeps incrementing
        start = get_stats_object.get_process_uptime_seconds
        time.sleep(1)
        assert get_stats_object.get_process_uptime_seconds > start

    def test_get_process_uptime_formatted(self, get_stats_object):
        assert_that(
            get_stats_object.get_process_uptime_formatted(),
            has_key('start_time')
        )
        assert_that(
            get_stats_object.get_process_uptime_formatted(),
            has_key('uptime')
        )
