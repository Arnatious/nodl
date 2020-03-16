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

from collections import namedtuple
from pathlib import Path
import pprint
import sys
from typing import Dict, List, Optional, TYPE_CHECKING

from ament_index_python.packages import get_package_share_directory, PackageNotFoundError
from nodl import parse as parse_nodl
import nodl.errors

if TYPE_CHECKING:
    import nodl.types


if TYPE_CHECKING:
    import argparse


class NoNoDLFilesError(Exception):
    """Exception raised when a package has no NoDL files in the ament index."""

    def __init__(self, package_name):
        super().__init__(f'{package_name} has no NoDL files in its ament index.')


def get_nodl_files_from_package_share(*, package_name: str) -> List[Path]:
    """
    Return all .nodl.xml files from the share directory of a package.

    :raises: PackageNotFoundError if package is not found
    :raises: NoNoDLFilesError if no .nodl.xml files are in package share directory
    """
    package_share_directory = Path(get_package_share_directory(package_name))
    nodl_paths = get_nodl_xml_files_in_path(path=package_share_directory)
    if not nodl_paths:
        raise NoNoDLFilesError(package_name)
    return nodl_paths


def get_nodl_xml_files_in_path(*, path: Path) -> List[Path]:
    """Return all files with NoDL extension (.nodl.xml) in a path."""
    return sorted(path.glob('**/*.nodl.xml'))


def _do_parse_nodl(*, path: Path) -> List[Path]:
    try:
        nodes = parse_nodl(path)
    except nodl.errors.InvalidNoDLDocumentError as e:
        print(f'Parsing of {path.name} failed', file=sys.stderr)
        print(e, file=sys.stderr)
        raise e
    return nodes


def show_nodl(*, paths: List[Path], raw: bool = False):
    """
    Print filename and either contents or NoDL data to console.

    :param paths: Name of nodl files to show
    :type paths: List[Path]
    :param raw: Whether to print file as-is or parse, defaults to False
    :type raw: bool, optional
    """
    if raw:
        show_nodl_raw(paths=paths)
    else:
        show_nodl_parsed(paths=paths)


def show_nodl_raw(*, paths: List[Path]):
    """
    Print filename and contents to console.

    :param paths: Names of nodl files to show
    :type paths: List[Path]
    """
    for path in paths:
        print(f'{path.name}:\n' + ('-' * 80) + '\n')
        print(path.read_text())


def show_nodl_parsed(*, paths: List[Path]) -> bool:
    """
    Print filename and contents to console.

    :param paths: Names of nodl file to show
    :type paths: List[Path]
    """
    try:
        node_lists = {path: parse_nodl(path) for path in paths}
    except nodl.errors.InvalidNoDLDocumentError:
        return False
    combined: Dict[str, '_NodeWithOrigin'] = {}
    for path, node_list in node_lists.items():
        for node in node_list:
            current_node = _NodeWithOrigin([path], node)
            if node.name not in combined:
                combined[node.name] = current_node
            else:
                try:
                    combined[node.name] += current_node
                except nodl.errors.NodeMergeConflictError:
                    _report_merge_error(current_node, combined[node.name])

                    return False
    pprint.pprint(node._as_dict)
    return True


def validate_nodl_file(*, path: Path) -> bool:
    """
    Validate the NoDL file at the given path by attempting to parse it.

    Requires `path` be a valid path.

    :param path: Path of an existing NoDL file.
    :type path: Path
    :return: Whether validation succeeded.
    :rtype: bool
    """
    try:
        parse_nodl(path)
    except nodl.errors.InvalidNoDLDocumentError as e:
        print(f'Validation of {str(path)} failed', file=sys.stderr)
        print(e, file=sys.stderr)
        return False
    return True


def _report_merge_error(current_node: '_NodeWithOrigin', existing_node: '_NodeWithOrigin'):
    print(
        (
            f'Failed to merge node "{current_node.node.name}" from {current_node.paths} ',
            f'with existing entry from {existing_node.paths}',
        ),
        file=sys.stderr,
    )
    print(
        (
            f'{current_node.paths[0]}:\n',
            f'{"-" * 80}\n',
            f'{pprint.pformat(current_node.node._as_dict)}\n',
            f'\n',
            f'{pprint.pformat(existing_node.paths)}:\n',
            f'{"-" * 80}\n',
            f'{pprint.pformat(existing_node.node._as_dict)}',
        ),
        file=sys.stderr,
    )


class NoDLFileNameCompleter:
    """Callable returning a list of nodl file names within a package's share directory."""

    def __init__(self, *, package_name_key: Optional[str] = None) -> None:
        self.package_name_key = 'package_name' if package_name_key is None else package_name_key

    def __call__(self, *, parsed_args: 'argparse.Namespace', **kwargs) -> List[str]:
        """
        Return a list of file names for nodl files found within the package.

        :param prefix: [description]
        :type prefix: str
        :param parsed_args: [description]
        :type parsed_args: [type]
        """
        package_name = getattr(parsed_args, self.package_name_key)
        try:
            return [
                path.name for path in get_nodl_files_from_package_share(package_name=package_name)
            ]
        except PackageNotFoundError:
            return ['package not found']


class _NodeWithOrigin:
    """Helper class to track the file(s) that a given node came from."""

    def __init__(self, paths: List[Path], node: 'nodl.types.Node') -> None:
        self.paths = paths
        self.node = node

    def __iadd__(self, other: '_NodeWithOrigin'):
        self.paths += other.paths
        self.node += other.node
