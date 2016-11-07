from flask import (
    Flask,
    send_file,
    render_template,
    request,
    Response,
    stream_with_context
)

import io
import psutil, os, magic
from lib.stats import Stats
from lib.http import validator, PartialFile
from settings import APP_ROOT, APP_STATIC, APP_ASSET

application = Flask(__name__)
stats = Stats(psutil.Process(os.getpid()))

@application.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response

@application.route("/download/<path:file_path>",  methods=['GET'])
@validator
def download(file_path, range_header):

    full_path = os.path.join(APP_ASSET,file_path)

    #return the whole file if range header does not exists
    if range_header is None:
        stats.add_bytes(PartialFile.get_length(full_path))
        return send_file(full_path)

    data = PartialFile()
    return_object = data.get_partial_file(full_path, range_header)
    stats.add_bytes(return_object.length)
    return Response(return_object.data, 206, direct_passthrough = True, headers = return_object.headers)

@application.route("/status")
def status():
    return render_template('status.html', stats = stats)

@application.errorhandler(Exception)
def all_exception_handler(error):
    message = "Exception Error"
    status_code = 500

    if hasattr(error, 'message'):
        message = error.message
    if hasattr(error, 'status_code'):
        status_code = error.status_code

    resp = Response(message , status_code)

    #4.4.  416 Range Not Satisfiable, return Content-Range
    if hasattr(error, 'length') and error.length and error.status_code == 416:
        resp.headers.add('Content-Range', 'bytes */{0}'.format(error.length))

    return resp

def send_file_partial(path):
    return "Hello World from Flask using Python 3.51"
if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True, port=80)
