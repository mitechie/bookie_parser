"""Tornado request handlers for our application."""
from tornado import httpclient
from tornado.web import asynchronous
from tornado.web import RequestHandler
from readability.readability import Document

from bookie_parser import TPL
from bookie_parser.logconfig import LOG


class MainHandler(RequestHandler):
    """The main index handler."""
    def get(self):
        """Get '/' for main site page."""
        self.content_type = 'text/html'
        t = TPL.load('index.html')
        self.write(t.generate())


class ReadableHandler(RequestHandler):
    """Readable parsing routes."""

    @asynchronous
    def get(self, url):
        """Getting will fetch the content for the url."""
        httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
        http = httpclient.AsyncHTTPClient()
        try:
            http.fetch(url, self._on_download)
        except httpclient.HTTPError, exc:
            LOG.error(e)

    def _on_download(self, response):
        """On downloading the url content, make sure we readable it."""
        LOG.info(response.request_time)
        self._readable_content(response.request.url, response.body)
        self.finish()

    def _readable_content(self, url, content):
        """Shared helper to process and respond with the content."""
        doc = Document(content)
        readable_article = doc.summary()
        try:
            readable_title = doc.short_title()
        except AttributeError, exc:
            LOG.error(str(exc))
            readable_title = 'Unknown'
        resp = {
            'url': url,
            'readable': readable_article,
            'title': readable_title,
        }
        self.content_type = 'application/json'
        self.write(resp)

    def post(self, url):
        """Posting content will have it parsed and fed back to you in JSON."""
        content = self.get_argument('content')
        self._readable_content(url, content)