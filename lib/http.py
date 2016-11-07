from functools import wraps
from flask import(
    request,
    json,
    current_app,
    Response
)
import os, re, itertools
from settings import APP_ASSET
from lib.utils import get_mime_type

def validator(return_func):
    @wraps(return_func)
    def decorated_function(*args, **kws):
        """
        Decorator to assert errors on whatever we would like to validate such
        as file exists, query parameter not matching header range param, etc..
        """
        #import pudb; pudb.set_trace()
        full_path = os.path.join(APP_ASSET, request.view_args['file_path'])

        if not os.path.exists(full_path):
            raise CustomHTTPError("File does not exists", 404)

        file_size = PartialFile.get_length(full_path)
        query_range = request.args.get('bytes', None)
        header_range = request.headers.get('Range', None)
        range_header = None

        if query_range and header_range and query_range != header_range:
            raise CustomHTTPError("Range Not Satisfiable", 416, file_size)

        #set range_header to either query_range or header_range
        if query_range is not None:
            range_header = query_range
        elif header_range is not None:
            range_header = header_range

        #filter and validate tuple in header
        if range_header is not None:
            range_header = PartialFile.filter_list(range_header)
            for r in range_header:
            #A byte-range-spec is invalid if the last-byte-pos value is present
            #and less than the first-byte-pos.
                first, last = PartialFile.set_range(r, file_size)
                if first > last:
                    raise CustomHTTPError("Range Not Satisfiable", 416, file_size)

        kws['range_header'] = range_header
        result = return_func(*args, **kws)
        return result

    return decorated_function

class PartialFile(object):

    @staticmethod
    def set_range(range_header, file_size):
        #parse range value
        # match = re.search('(\d*)-(\d*)', range_header)
        # range_values = match.groups()
        first = ''
        last = ''

        if range_header[0] is not '':
            first = int(range_header[0])

        if range_header[1] is not '':
            last = int(range_header[1])

        if first is '':
            suffix = last
            last = file_size - 1
            first = file_size - suffix
            if first < 0:
                first = 0
        else:
            if last is '' or last > file_size - 1:
                last = file_size - 1
        return [first, last]

    @staticmethod
    def get_length(file_path):
        # An asterisk character ("*") in place of the complete-length indicates
        #that the representation length was unknown when the header field wasgenerated.
        length = os.path.getsize(file_path)
        if length:
            return length
        return '*'

    @staticmethod
    def filter_list(range_list):
        """
        Expects a list of string values ['100-500', '400-600', '300-900', '1000-2000']
        """
        range_item = []

        range_list = range_list.split(",")
        for r in range_list:
            first = ''
            last = ''
            match = re.search('(\d*)-(\d*)', r)
            range_values = match.groups()

            if range_values[0] and not '':
                first = int(range_values[0])
            if range_values[1] and not '':
                last = int(range_values[1])

            range_item.append((first, last))
        #if there is missing first or last specified, return input list
        if not first or not last:
            return range_item
        #sort tuple for coalescing
        sorted_tuple = sorted(range_item, key=lambda x: x[0])
        return_items = []
        size = len(sorted_tuple) - 1
        idx = 0
        if not size:
            return sorted_tuple

        for idx, val in enumerate(sorted_tuple):
            #check to see if second value in tuple is larger than next values
            #merge if condition is satisfied
            if idx < size:
                if sorted_tuple[idx][1] > sorted_tuple[idx+1][0]:
                    if sorted_tuple[idx][1] < sorted_tuple[idx+1][1]:
                        val = (sorted_tuple[idx][0], sorted_tuple[idx+1][1])
                        return_items.append(val)

                    sorted_tuple[idx+1] = val
                elif idx == 0:
                    return_items.append(sorted_tuple[idx])
            elif idx == size:
                return_items.append(sorted_tuple[idx])
            #idx += 1
        return return_items

    def get_multipart_content(self, range_list, file_size, file_path, boundry, content_type):
        length = 0
        data = str.encode('')
        for range_header in range_list:
            start, end = PartialFile.set_range(
                range_header,
                file_size
            )
            build_start = '\r\n--{0}\r\n'.format(boundry)
            data += str.encode(build_start)
            length += len(build_start)
            build_set_type = 'Content-Type: {0}\r\n'.format(content_type)
            data += str.encode(build_set_type)
            length += len(build_set_type)
            build_set_range = 'Content-Range: bytes {0}-{1}/{2}\r\n\r\n'.format(
                start,
                end,
                file_size
                )
            data += str.encode(build_set_range)
            length += len(build_set_range)

            data += self.get_file_stream(file_path, start, end-start+1)
            length += end-start+1;

        build_end = '\r\n--{0}--\r\n'.format(boundry)
        data += str.encode(build_end)
        length += len(build_end)
        return [length, data]


    def get_file_stream(self, file_path, start, length):
        data = None
        with open(file_path, 'rb') as f:
            f.seek(start)
            data = f.read(length)
        return data


    def get_partial_file(self, file_path, range_header):
        """
        Seeks the range of file and return specified range bytes
        """
        file_size = PartialFile.get_length(file_path)
        content_type = get_mime_type(file_path)
        #check for multipart/byteranges
        # Content-Type: multipart/byteranges; boundary=THIS_STRING_SEPARATES
        if len(range_header) > 1:
            #create random boundry
            boundry = 'THIS_STRING_SEPARATES';

            length, data = self.get_multipart_content(
                range_header,
                file_size,
                file_path,
                boundry,
                content_type
            )
            self.data = data
            self.length = length
            self.headers = {
                'Content-Type': "multipart/x-byteranges; boundary={0}".format(boundry),
                'Content-Length':length
            }

        else:
            #range_tuple = PartialFile.filter_list([range_header])
            start, end = PartialFile.set_range(
                range_header[0],
                file_size
            )

            length = end - start + 1
            self.data = self.get_file_stream(file_path, start, length)
            self.length  = length
            self.headers = {
                'Content-Type': content_type,
                'Content-Length':length,
                'Content-Range':'bytes {0}-{1}/{2}'.format(
                    start,
                    start + length - 1,
                    file_size
                )
            }
        return self

class CustomHTTPError(Exception):
    """Exception raised for header range and query range mismatch.
    Attributes:
        message: explanation of the error
        status_code: status_code to repond to http call
    """

    def __init__(self, message, status_code = 416, length = None):
        self.message = message
        self.status_code = status_code
        self.length = length

    def message(self):
        return self.message
