import unittest

import httpretty

import threatingestor.sources.web


class TestWeb(unittest.TestCase):

    def setUp(self):
        self.web = threatingestor.sources.web.Plugin('myweb', 'http://example.mock/list.txt')

    @httpretty.activate
    def test_run_with_200(self):
        httpretty.register_uri(httpretty.HEAD, "http://example.mock/list.txt")
        httpretty.register_uri(httpretty.GET, "http://example.mock/list.txt",
                body='http://example.com/test',
                adding_headers={
                    'Last-Modified': 'test',
                    'Etag': '"test"'
                })

        saved_state, artifacts = self.web.run(None)
        self.assertIn('http://example.com/test', [str(x) for x in artifacts])
        self.assertEquals(saved_state, 'test;"test"')

    @httpretty.activate
    def test_run_with_304(self):
        httpretty.register_uri(httpretty.HEAD, "http://example.mock/list.txt",
                               status=304)

        saved_state, artifacts = self.web.run('test;"test"')
        self.assertEquals(len(artifacts), 0)

    @httpretty.activate
    def test_run_with_200_and_no_etag(self):
        httpretty.register_uri(httpretty.HEAD, "http://example.mock/list.txt")
        httpretty.register_uri(httpretty.GET, "http://example.mock/list.txt",
                body='http://example.com/test',
                adding_headers={
                    'Last-Modified': 'test',
                })

        saved_state, artifacts = self.web.run(None)
        self.assertIn('http://example.com/test', [str(x) for x in artifacts])
        self.assertEquals(saved_state, 'test')
