import pytest
import application as app

@pytest.fixture
def client():
    return app.application.test_client()

def test_status_end_point(client):
    resp = client.get('/status')
    assert resp.status_code == 200
def test_download_only_get_method(client):
    resp = client.post('/download/video_test.mov?bytes=0-999')
    #method not allowed
    assert resp.status_code == 405

def test_download_with_missing_file(client):
    #file video_test123 does not exist in assets directory
    resp = client.get('/download/video_test123.mov?bytes=0-999')
    assert resp.status_code == 404

def test_download_with_query_not_matching_header_range(client):
    #making sure 416 is returned if range header does not match ranger query parameter
    #2. HTTP 416 error must be returned in case where both header and query parameter are specified, but with a different value.
    resp = client.get('/download/video_test.mov?bytes=0-999', headers={'Range':'0-9991'})
    assert resp.status_code == 416

def test_download_with_no_query_and_no_header_range(client):
    #making sure 416 is returned if range header does not match ranger query parameter
    #2. HTTP 416 error must be returned in case where both header and query parameter are specified, but with a different value.
    resp = client.get('/download/video_test.mov')
    assert resp.status_code == 200

def test_download_end_point_success_with_query_params(client):
    resp = client.get('/download/video_test.mov?bytes=0-999')
    assert resp.status_code == 206

def test_download_end_point_success_with_header_params(client):
     resp = client.get('/download/video_test.mov', headers={'Range':'0-9991'})
     headers = dict(resp.headers)

     assert resp.status_code == 206
     assert headers['Content-Length'] == '9992'


def test_download_params(client):
    """
     Additional examples, assuming a representation of length 10000:

   o  The final 500 bytes (byte offsets 9500-9999, inclusive):

        bytes=-500

   Or:

        bytes=9500-

   o  The first and last bytes only (bytes 0 and 9999):

        bytes=0-0,-1

   o  Other valid (but not canonical) specifications of the second 500
      bytes (byte offsets 500-999, inclusive):

        bytes=500-600,601-999
        bytes=500-700,601-999
    """
    resp = client.get('/download/video_test.mov', headers={'Range':'-500'})
    assert resp.status_code == 206
    #'bytes 408499518-408500017/408500018'
    resp = client.get('/download/video_test.mov', headers={'Range':'9500-'})
    #'bytes 9500-408500017/408500018'
    assert resp.status_code == 206

    resp = client.get('/download/video_test.mov', headers={'Range':'0-0,-1'})

    assert resp.status_code == 206

    resp = client.get('/download/video_test.mov', headers={'Range':'900-700'})
    assert resp.status_code == 416

    resp = client.get('/download/video_test.mov', headers={'Range':'500-600,601-999'})
#     #out of range requests
#     #coalesce
