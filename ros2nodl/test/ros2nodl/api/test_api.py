# Copyright 2020 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU Limited General Public License version 3, as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranties of MERCHANTABILITY, SATISFACTORY QUALITY, or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Limited General Public License for more details.
#
# You should have received a copy of the GNU Limited General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

from pathlib import Path
import tempfile
from unittest.mock import NonCallableMagicMock

import nodl.types
import pytest
import ros2nodl.api


@pytest.fixture
def sample_package() -> tempfile.TemporaryDirectory:
    tmpdir = tempfile.TemporaryDirectory()
    tmppath = Path(tmpdir.name)
    shortnames = [
        'foo.nodl.xml',
        'bar.nodl.xml',
        'baz.xml.nodl',
        'fizz.nodl',
        'buzz.xml',
        'jonodl.xml',
    ]
    names = [(tmppath / name) for name in shortnames]
    for name in names:
        name.touch()
    return tmpdir


def test_show_nodl_raw(capsys):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_fake_nodl:
        tmp_fake_nodl.write(bytes(f'test@output\n', encoding='utf8'))
        tmp_fake_nodl.close()
        ros2nodl.api.show_nodl_raw(paths=[Path(tmp_fake_nodl.name)])
        assert 'test@output\n' in capsys.readouterr().out


def test_show_nodl_parsed(mocker, capsys):
    # Test invalid files raise NodeMergeConflcitError
    # Note: explicitly mocking the exception is required for `raise` to not error
    mock_exception = nodl.errors.DuplicateNodeError(
        node=mocker.Mock(),
    )
    mock = mocker.patch('ros2nodl.api.api.nodl.parse_multiple', side_effect=mock_exception)
    with pytest.raises(nodl.errors.DuplicateNodeError):
        ros2nodl.api.show_nodl_parsed(paths=[])

    # Test a valid call prints the _as_dict field
    node = NonCallableMagicMock(spec=nodl.types.Node, **{'_as_dict': 'foobar'})
    mock.side_effect = None
    mock.return_value = [node]
    ros2nodl.api.show_nodl_parsed(paths=[])
    assert 'foobar' in capsys.readouterr().out


def test__report_merge_error():
    pass
