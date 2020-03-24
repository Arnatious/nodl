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


def test_get_nodl_xml_files_in_path(sample_package):
    tmppath = Path(sample_package.name)

    result = ros2nodl.api.get_nodl_xml_files_in_path(path=tmppath)
    assert len(result) == 2
    assert all(path.name.endswith('.nodl.xml') for path in result)


def test_get_nodl_files_from_package_share(mocker, sample_package):
    mock = mocker.patch(
        'ros2nodl.api.api.get_package_share_directory', return_value=sample_package.name
    )
    result = ros2nodl.api.get_nodl_files_from_package_share(package_name='foo')
    mock.assert_called_with('foo')
    assert len(result) == 2
    assert all(path.name.endswith('.nodl.xml') for path in result)

    with tempfile.TemporaryDirectory() as tmpdir:
        mock.return_value = tmpdir
        with pytest.raises(ros2nodl.api.NoNoDLFilesError):
            ros2nodl.api.get_nodl_files_from_package_share(package_name='foo')


def test_show_nodl_raw(capsys):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_fake_nodl:
        tmp_fake_nodl.write(bytes(f'test@output\n', encoding='utf8'))
        tmp_fake_nodl.close()
        ros2nodl.api.show_nodl_raw(paths=[Path(tmp_fake_nodl.name)])
        assert 'test@output\n' in capsys.readouterr().out


def test__merge_nodl_files(mocker):
    foo_action = nodl.types.Action(name='foo_action', action_type='foo_action_type')
    bar_action = nodl.types.Action(name='bar_action', action_type='bar_action_type')
    bar_topic = nodl.types.Topic(name='bar_topic', message_type='bar_topic_type')

    foo = nodl.types.Node(name='foo', actions=[foo_action])
    bar = nodl.types.Node(name='bar', actions=[bar_action])
    baz = nodl.types.Node(
        name='baz', actions=[nodl.types.Action(name='baz_action', action_type='baz_action_type')]
    )
    kni = nodl.types.Node(name='bar', topics=[bar_topic])
    shr = nodl.types.Node(
        name='baz', actions=[nodl.types.Action(name='baz_action', action_type='baz_action_type_2')]
    )
    # Test 2 cases
    # foo x foo -> identical merge
    # bar x kni -> same node name, unique interfaces
    return_iterable = [[foo, bar, baz], [foo, kni]]
    mock_parse_nodl = mocker.patch('ros2nodl.api.api.parse_nodl', side_effect=return_iterable)

    result = ros2nodl.api.api._merge_nodl_files(paths=['alpha', 'beta'])

    # Test case 1 - identical merge - no changes performed
    foo = next(filter(lambda node: node.name == 'foo', result))
    assert len(foo.actions) == 1
    assert foo_action in foo.actions.values()

    # Test case 2 - valid merge - new interface added
    bar = next(filter(lambda node: node.name == 'bar', result))
    assert len(bar.actions) == 1
    assert bar_action in bar.actions.values()
    assert len(bar.topics) == 1
    assert bar_topic in bar.topics.values()

    # Failing test case
    # baz x shr - different action types
    mock_parse_nodl.side_effect = [[baz], [shr]]
    with pytest.raises(nodl.errors.NodeMergeConflictError):
        result = ros2nodl.api.api._merge_nodl_files(paths=['alpha', 'beta'])


def test_show_nodl_parsed(mocker, capsys):
    # Test invalid files raise NodeMergeConflcitError
    # Note: explicitly mocking the exception is required for `raise` to not error
    mock_exception = nodl.errors.NodeMergeConflictError(
        node_a=mocker.Mock(),
        node_b=mocker.Mock(),
        interface_a=mocker.Mock(),
        interface_b=mocker.Mock(),
    )
    mock = mocker.patch('ros2nodl.api.api._merge_nodl_files', side_effect=mock_exception)
    with pytest.raises(nodl.errors.NodeMergeConflictError):
        ros2nodl.api.show_nodl_parsed(paths=[])

    # Test a valid call prints the _as_dict field
    node = NonCallableMagicMock(spec=nodl.types.Node, **{'_as_dict': 'foobar'})
    mock.side_effect = None
    mock.return_value = [node]
    ros2nodl.api.show_nodl_parsed(paths=[])
    assert 'foobar' in capsys.readouterr().out


def test__report_merge_error():
    pass
