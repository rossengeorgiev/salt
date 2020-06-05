# -*- coding: utf-8 -*-
"""
    :codeauthor: Gareth J. Greenaway <gareth@saltstack.com>
"""

# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals

import logging

# Import Salt Libs
import salt.modules.zenoss as zenoss

# Import Salt Testing Libs
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.mock import MagicMock, patch
from tests.support.unit import TestCase

log = logging.getLogger(__name__)


class MockRequests(object):
    """
    Mock requests class
    """

    flag = None
    content = """{"message": "Invalid token", "errors": [{"type": "invalid_token", "subject": "token"}]}"""
    status_code = None

    def __init__(self):
        self.sess = None
        self.url = None
        self.data = None
        self.kwargs = None

    def return_session(self, url, data=None, **kwargs):
        """
        Mock session method.
        """
        self.url = url
        self.data = data
        self.kwargs = kwargs

        if not self.sess:
            self.sess = MockRequests()

        if self.flag == 1:
            self.sess.status_code = 401
        else:
            self.sess.status_code = 200

        self.sess.headers = {}
        if self.content:
            self.sess.content = self.content

        return self.sess

    def session(self):
        """
        Mock session method.
        """
        self.sess = MockRequests()
        self.sess.headers = {}
        self.sess.auth = {}

        return self.sess

    def post(self, url, data=None, **kwargs):
        """
        Mock post method.
        """
        return self.return_session(url, data, **kwargs)

    def delete(self, url, **kwargs):
        """
        Mock delete method.
        """
        return self.return_session(url, **kwargs)

    def get(self, url, **kwargs):
        """
        Mock get method.
        """
        return self.return_session(url, **kwargs)

    def put(self, url, data=None, **kwargs):
        """
        Mock put method.
        """
        return self.return_session(url, data, **kwargs)


class ZenossTestCase(TestCase, LoaderModuleMockMixin):
    """
    Test cases for salt.modules.zenoss
    """

    def setup_loader_modules(self):
        return {zenoss: {"requests": MockRequests()}}

    def test__session_apikey(self):
        """
        Test api_key is passed correct via session headers
        """
        mock_cmd = MagicMock(
            return_value={"hostname": "zenoss", "api_key": "FFFFFFFFFFFFFFFFFFFFFFFFFF"}
        )

        with patch.dict(zenoss.__salt__, {"config.option": mock_cmd}):
            session = zenoss._session()

            self.assertIn("z-api-key", session.headers)
            self.assertEqual(session.headers["z-api-key"], "FFFFFFFFFFFFFFFFFFFFFFFFFF")

            self.assertIn("Content-type", session.headers)
            self.assertEqual(
                session.headers["Content-type"], "application/json; charset=utf-8"
            )

    def test__session_username_password(self):
        """
        Test username and password is passed correct via session headers
        """
        mock_cmd = MagicMock(
            return_value={
                "hostname": "zenoss",
                "username": "username",
                "password": "password",
            }
        )

        with patch.dict(zenoss.__salt__, {"config.option": mock_cmd}):
            session = zenoss._session()

            self.assertEqual(session.auth, ("username", "password"))

            self.assertIn("Content-type", session.headers)
            self.assertEqual(
                session.headers["Content-type"], "application/json; charset=utf-8"
            )

    def test_find_device(self):
        """
        Test find device
        """
        mock_cmd = MagicMock(
            return_value={
                "hostname": "zenoss",
                "username": "username",
                "password": "password",
            }
        )

        with patch.dict(zenoss.__salt__, {"config.option": mock_cmd}):
            MockRequests.content = """{"result": {"devices": [{"name": "hostname1"},
                                                              {"name": "hostname2"}],
                                                  "hash": "47ebaaf096c749c92597f05bde625f1e"}}"""
            expected = {"name": "hostname1", "hash": "47ebaaf096c749c92597f05bde625f1e"}
            request = zenoss.find_device("hostname1")
            self.assertEqual(request, expected)

        with patch.dict(zenoss.__salt__, {"config.option": mock_cmd}):
            MockRequests.content = """{"result": {"devices": [{"name": "hostname1"},
                                                              {"name": "hostname2"}],
                                                  "hash": "47ebaaf096c749c92597f05bde625f1e"}}"""
            request = zenoss.find_device("hostname3")
            self.assertEqual(request, None)

        mock_cmd = MagicMock(
            return_value={"hostname": "zenoss", "api_key": "FFFFFFFFFFFFFFFFFFFFFFFFFF"}
        )

        with patch.dict(zenoss.__salt__, {"config.option": mock_cmd}):
            MockRequests.content = """{"result": {"devices": [{"name": "hostname1"},
                                                              {"name": "hostname2"}],
                                                  "hash": "47ebaaf096c749c92597f05bde625f1e"}}"""
            expected = {"name": "hostname1", "hash": "47ebaaf096c749c92597f05bde625f1e"}
            request = zenoss.find_device("hostname1")
            self.assertEqual(request, expected)

        with patch.dict(zenoss.__salt__, {"config.option": mock_cmd}):
            MockRequests.content = """{"result": {"devices": [{"name": "hostname1"},
                                                              {"name": "hostname2"}],
                                                  "hash": "47ebaaf096c749c92597f05bde625f1e"}}"""
            request = zenoss.find_device("hostname3")
            self.assertEqual(request, None)
