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
import warnings
from datetime import datetime, timezone

from superset.utils.dates import utcnow


def test_utcnow_returns_naive_datetime() -> None:
    result = utcnow()
    assert isinstance(result, datetime)
    assert result.tzinfo is None


def test_utcnow_matches_aware_utc_now() -> None:
    aware_before = datetime.now(timezone.utc)
    naive = utcnow()
    aware_after = datetime.now(timezone.utc)

    naive_before = aware_before.replace(tzinfo=None)
    naive_after = aware_after.replace(tzinfo=None)

    assert naive_before <= naive <= naive_after


def test_utcnow_does_not_emit_deprecation_warning() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        # If the implementation regressed to ``datetime.utcnow()`` this would
        # raise ``DeprecationWarning`` on Python 3.12+ and fail the test.
        utcnow()
