import magic
from datetime import datetime, timedelta

def get_mime_type(file_path):
    mime = magic.Magic(mime = True)
    content_type = mime.from_file(file_path)
    return content_type



def format_seconds_to_date(seconds):
    sec = timedelta(seconds = int(seconds))
    d = datetime(1,1,1) + sec

    return "Days: {0}, Hours: {1}, Minutes: {2}, Seconds: {3}".format(d.day-1, d.hour, d.minute, d.second)
