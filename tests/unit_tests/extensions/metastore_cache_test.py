# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

import logging
from typing import Any

import pytest
from pytest_mock import MockerFixture

from superset.extensions.metastore_cache import SupersetMetastoreCache
from superset.key_value.types import (
    JsonKeyValueCodec,
    PickleKeyValueCodec,
)


@pytest.fixture
def factory_kwargs(mocker: MockerFixture) -> dict[str, Any]:
    """
    Build the args/kwargs dict expected by ``SupersetMetastoreCache.factory``.

    ``get_uuid_namespace`` is patched so the factory does not need to read a
    real Flask app config for ``HASH_ALGORITHM``.
    """
    mocker.patch(
        "superset.extensions.metastore_cache.get_uuid_namespace",
        return_value=mocker.sentinel.namespace,
    )
    return {"args": [], "kwargs": {}, "app": mocker.Mock()}


def test_factory_default_codec_is_json(
    mocker: MockerFixture, factory_kwargs: dict[str, Any]
) -> None:
    mocker.patch(
        "superset.extensions.metastore_cache.has_app_context", return_value=False
    )

    cache = SupersetMetastoreCache.factory(
        app=factory_kwargs["app"],
        config={},
        args=factory_kwargs["args"],
        kwargs=factory_kwargs["kwargs"],
    )

    assert isinstance(cache, SupersetMetastoreCache)
    assert isinstance(cache.codec, JsonKeyValueCodec)
    assert not isinstance(cache.codec, PickleKeyValueCodec)


def test_factory_respects_explicit_codec(
    mocker: MockerFixture, factory_kwargs: dict[str, Any]
) -> None:
    mocker.patch(
        "superset.extensions.metastore_cache.has_app_context", return_value=False
    )
    explicit = JsonKeyValueCodec()

    cache = SupersetMetastoreCache.factory(
        app=factory_kwargs["app"],
        config={"CODEC": explicit},
        args=factory_kwargs["args"],
        kwargs=factory_kwargs["kwargs"],
    )

    assert cache.codec is explicit


def test_factory_default_does_not_warn_about_pickle(
    mocker: MockerFixture,
    factory_kwargs: dict[str, Any],
    caplog: pytest.LogCaptureFixture,
) -> None:
    mocker.patch(
        "superset.extensions.metastore_cache.has_app_context", return_value=True
    )
    mock_current_app = mocker.patch("superset.extensions.metastore_cache.current_app")
    mock_current_app.debug = False

    with caplog.at_level(logging.WARNING, logger="superset.extensions.metastore_cache"):
        SupersetMetastoreCache.factory(
            app=factory_kwargs["app"],
            config={},
            args=factory_kwargs["args"],
            kwargs=factory_kwargs["kwargs"],
        )

    assert "PickleKeyValueCodec" not in caplog.text


def test_factory_warns_when_pickle_explicitly_configured(
    mocker: MockerFixture,
    factory_kwargs: dict[str, Any],
    caplog: pytest.LogCaptureFixture,
) -> None:
    mocker.patch(
        "superset.extensions.metastore_cache.has_app_context", return_value=True
    )
    mock_current_app = mocker.patch("superset.extensions.metastore_cache.current_app")
    mock_current_app.debug = False

    with caplog.at_level(logging.WARNING, logger="superset.extensions.metastore_cache"):
        SupersetMetastoreCache.factory(
            app=factory_kwargs["app"],
            config={"CODEC": PickleKeyValueCodec()},
            args=factory_kwargs["args"],
            kwargs=factory_kwargs["kwargs"],
        )

    assert (
        "PickleKeyValueCodec with SupersetMetastoreCache may be unsafe" in caplog.text
    )
