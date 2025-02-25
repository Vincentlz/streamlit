# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2025)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import unittest
from unittest.mock import PropertyMock, mock_open, patch

import pytest

import streamlit as st
from streamlit.connections import BaseConnection
from streamlit.runtime.secrets import AttrDict

MOCK_TOML = """
[connections.my_mock_connection]
foo="bar"
"""


class MockRawConnection:
    def some_raw_connection_method(self):
        return "some raw connection method"


class MockConnection(BaseConnection[str]):
    def _connect(self, **kwargs) -> str:
        return MockRawConnection()

    def some_method(self):
        return "some method"


class BaseConnectionDefaultMethodTests(unittest.TestCase):
    def setUp(self) -> None:
        # st.secrets modifies os.environ, so we save it here and
        # restore in tearDown.
        self._prev_environ = dict(os.environ)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._prev_environ)
        st.secrets._reset()

    def test_instance_set_to_connect_return_value(self):
        assert isinstance(
            MockConnection("my_mock_connection")._instance, MockRawConnection
        )

    def test_getattr_works_with_methods_on_connection(self):
        assert MockConnection("my_mock_connection").some_method() == "some method"

    def test_getattr_friendly_error_message(self):
        with pytest.raises(AttributeError) as e:
            MockConnection("my_mock_connection").some_raw_connection_method()

        assert (
            str(e.value)
            == "`some_raw_connection_method` doesn't exist here, but you can call `._instance.some_raw_connection_method` instead"
        )
        assert (
            MockConnection("my_mock_connection")._instance.some_raw_connection_method()
            == "some raw connection method"
        )

    def test_getattr_totally_nonexistent_attr(self):
        with pytest.raises(AttributeError) as e:
            MockConnection("my_mock_connection").totally_nonexistent_method()

        assert (
            str(e.value)
            == "'MockConnection' object has no attribute 'totally_nonexistent_method'"
        )

    @patch("builtins.open", new_callable=mock_open, read_data=MOCK_TOML)
    def test_secrets_property(self, _):
        conn = MockConnection("my_mock_connection")
        assert conn._secrets.foo == "bar"

    @patch("builtins.open", new_callable=mock_open, read_data=MOCK_TOML)
    def test_secrets_property_no_matching_section(self, _):
        conn = MockConnection("nonexistent")
        assert conn._secrets == {}

    def test_secrets_property_no_secrets(self):
        conn = MockConnection("my_mock_connection")
        assert conn._secrets == {}

    def test_instance_prop_caches_raw_instance(self):
        conn = MockConnection("my_mock_connection")
        conn._raw_instance = "some other value"

        assert conn._instance == "some other value"

    def test_instance_prop_reinitializes_if_reset(self):
        conn = MockConnection("my_mock_connection")
        conn._raw_instance = None

        assert isinstance(conn._instance, MockRawConnection)

    def test_on_secrets_changed_when_nothing_changed(self):
        conn = MockConnection("my_mock_connection")

        # conn.reset() shouldn't be called because secrets haven't changed since conn
        # was constructed.
        with patch(
            "streamlit.connections.base_connection.BaseConnection.reset"
        ) as patched_reset:
            conn._on_secrets_changed("unused_arg")
            patched_reset.assert_not_called()

    def test_on_secrets_changed(self):
        conn = MockConnection("my_mock_connection")

        with patch(
            "streamlit.connections.base_connection.BaseConnection.reset"
        ) as patched_reset, patch(
            "streamlit.connections.base_connection.BaseConnection._secrets",
            PropertyMock(return_value=AttrDict({"mock_connection": {"new": "secret"}})),
        ):
            conn._on_secrets_changed("unused_arg")
            patched_reset.assert_called_once()

    # Test this here rather than in write_test.py because the MockConnection object
    # is defined here. Seems cleaner.
    def test_st_write(self):
        conn = MockConnection("my_mock_connection")

        with patch("streamlit.delta_generator.DeltaGenerator.help") as p:
            st.write(conn)

            p.assert_called_once_with(conn)
