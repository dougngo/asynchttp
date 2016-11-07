from gevent.pywsgi import WSGIServer
from gevent import monkey
monkey.patch_all()

from psycogreen.gevent import patch_psycopg
patch_psycopg()

import application as app
application = app.application

http_server = WSGIServer(('', 80), application)
http_server.serve_forever()
