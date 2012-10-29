"""Readable is response we're passing back based on our work here.

We need to provide back to the caller

- url
- is_error
- content
- content_type
- headers (response)
- status_message (Ok)
- status_code (200)
- domain
- request_time

"""
import hashlib
import pytz
import requests

from datetime import datetime
from dateutil import parser
from httpcode import STATUS_CODES
from requests import ConnectionError
from urlparse import urlparse


def generate_hash(url_string):
    m = hashlib.sha256()
    m.update(url_string)
    return m.hexdigest()[:14]


class ReadableRequest(object):
    """Fetch a url and handle the response."""

    def __init__(self, url):
        self.url = url

    def __iter__(self):
        keys = ['content', 'content_type', 'domain',
                'final_url', 'headers', 'is_error',
                'request_time', 'status_code', 'url']
        for key in keys:
            yield(key, getattr(self, key))

    def process(self):
        self.start_time = datetime.utcnow()
        self.start_time = self.start_time.replace(tzinfo=pytz.utc)

        try:
            response = requests.get(self.url)
            self.status_code = response.status_code
            self.content = response.text
            self.content_type = response.headers['content-type']
            self.headers = response.headers
            self.final_url = response.url
            self.domain = urlparse(self.final_url).netloc
            request_time = parser.parse(response.headers['date'])
        except ConnectionError:
            # Set us up with a nice failure setup.
            self.status_code = 500
            request_time = datetime.utcnow().replace(tzinfo=pytz.utc)

        elapsed = (request_time - self.start_time).microseconds / 1000000.0
        self.request_time = elapsed

    @property
    def is_error(self):
        """Verify our status code is an error/not."""
        # simple first check, if it's not a 2xx, then it's an error
        return False if str(self.status_code).startswith('2') else True

    @property
    def status_message(self):
        """Fetch the status message from the httpcode library."""
        # This is a tuple of short message, long message. We only care for the
        # short version.
        return STATUS_CODES[self.status_code][0]
