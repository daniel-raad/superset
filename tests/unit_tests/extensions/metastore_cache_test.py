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
from unittest.mock import Mock

import pytest

from superset.extensions.metastore_cache import SupersetMetastoreCache
from superset.key_value.types import (
    JsonKeyValueCodec,
    PickleKeyValueCodec,
)


def _make_app() -> Mock:
    app = Mock()
    app.config = {"CACHE_KEY_PREFIX": "test_prefix", "HASH_ALGORITHM": "sha256"}
    return app


def test_factory_defaults_to_json_codec() -> None:
    app = _make_app()
    kwargs: dict[str, object] = {}
    cache = SupersetMetastoreCache.factory(
        app=app,
        config={"CACHE_KEY_PREFIX": "test_prefix"},
        args=[],
        kwargs=kwargs,
    )
    assert isinstance(cache, SupersetMetastoreCache)
    assert isinstance(kwargs["codec"], JsonKeyValueCodec)
    assert not isinstance(kwargs["codec"], PickleKeyValueCodec)


def test_factory_respects_explicit_codec() -> None:
    app = _make_app()
    explicit_codec = PickleKeyValueCodec()
    kwargs: dict[str, object] = {}
    SupersetMetastoreCache.factory(
        app=app,
        config={"CACHE_KEY_PREFIX": "test_prefix", "CODEC": explicit_codec},
        args=[],
        kwargs=kwargs,
    )
    assert kwargs["codec"] is explicit_codec


def test_factory_warns_when_pickle_codec_is_explicit(
    caplog: pytest.LogCaptureFixture,
) -> None:
    app = _make_app()
    kwargs: dict[str, object] = {}
    with caplog.at_level(logging.WARNING, logger="superset.extensions.metastore_cache"):
        SupersetMetastoreCache.factory(
            app=app,
            config={
                "CACHE_KEY_PREFIX": "test_prefix",
                "CODEC": PickleKeyValueCodec(),
            },
            args=[],
            kwargs=kwargs,
        )
    warning_message = "PickleKeyValueCodec with SupersetMetastoreCache may be unsafe"
    assert any(warning_message in record.message for record in caplog.records)


def test_factory_does_not_warn_for_default_json_codec(
    caplog: pytest.LogCaptureFixture,
) -> None:
    app = _make_app()
    kwargs: dict[str, object] = {}
    with caplog.at_level(logging.WARNING, logger="superset.extensions.metastore_cache"):
        SupersetMetastoreCache.factory(
            app=app,
            config={"CACHE_KEY_PREFIX": "test_prefix"},
            args=[],
            kwargs=kwargs,
        )
    warning_message = "PickleKeyValueCodec with SupersetMetastoreCache may be unsafe"
    assert not any(warning_message in record.message for record in caplog.records)
