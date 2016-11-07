import time
from lib.utils import format_seconds_to_date

class Stats(object):
    def __init__(self, process):
        self.bytes_streamed = 0
        self.start_time = int(process.create_time())

    def add_bytes(self, streamed):
        self.bytes_streamed += streamed

    def get_bytes_streamed(self):
        return self.bytes_streamed

    @property
    def get_process_uptime_seconds(self):
        return time.time() - self.start_time

    def get_process_uptime_formatted(self):
        """
            method to return formatted days, hours, minutes uptime and value
            formatted date when process was started
        """
        seconds = self.get_process_uptime_seconds
        start_time = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(self.start_time)
        )

        return {'start_time':start_time, 'uptime':format_seconds_to_date(seconds)}
