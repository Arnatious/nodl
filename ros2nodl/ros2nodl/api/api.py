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
import pprint
from typing import Dict, List, Optional, TYPE_CHECKING

from ament_index_python.packages import get_package_share_directory, PackageNotFoundError
from nodl import parse as parse_nodl
import nodl.errors

if TYPE_CHECKING:  # pragma: no cover
    import nodl.types
    import argparse


class NoNoDLFilesError(Exception):
    """Exception raised when a package has no NoDL files in the ament index."""

    def __init__(self, package_name):
        super().__init__(f'{package_name} has no NoDL files in its ament index.')


class FailedMergeError(nodl.errors.NodeMergeConflictError):

    def __init__(self, error: nodl.errors.NodeMergeConflictError) -> None:
        msg = (
            f'Failed to merge node "{error.node_a.name}" from {error.node_a.paths} ',
            f'with existing entry from {error.node_b.paths}\n',
            f'{error.node_a.paths[0]}:\n',
            f'{"-" * 80}\n',
            f'{pprint.pformat(error.node_a._as_dict)}\n',
            f'\n',
            f'{pprint.pformat(error.node_b.paths)}:\n',
            f'{"-" * 80}\n',
            f'{pprint.pformat(error.node_b._as_dict)}',
        )
        super().__init__(
            msg=msg,
            node_a=error.node_a,
            node_b=error.node_b,
            interface_a=error.interface_a,
            interface_b=error.interface_b,
        )


def get_nodl_xml_files_in_path(*, path: Path) -> List[Path]:
    """Return all files with NoDL extension (.nodl.xml) in a path."""
    return sorted(path.glob('**/*.nodl.xml'))


def get_nodl_files_from_package_share(*, package_name: str) -> List[Path]:
    """
    Return all .nodl.xml files from the share directory of a package.

    :raises PackageNotFoundError: if package is not found
    :raises NoNoDLFilesError: if no .nodl.xml files are in package share directory
    """
    package_share_directory = Path(get_package_share_directory(package_name))
    nodl_paths = get_nodl_xml_files_in_path(path=package_share_directory)
    if not nodl_paths:
        raise NoNoDLFilesError(package_name)
    return nodl_paths


def show_nodl_raw(*, paths: List[Path]):
    """
    Print filename and contents to console.

    :param paths: Names of nodl files to show
    :type paths: List[Path]
    """
    for path in paths:
        print(f'{path.name}:\n' + ('-' * 80) + '\n')
        print(path.read_text())


def _merge_nodl_files(*, paths: List[Path]) -> 'List[nodl.types.Node]':
    """
    Recursively merge any nodes with the same name across multiple files.

    :raises e: NodeMergeConflictError if merge conflict occurs
    :return: List of nodes from all input files, with same name nodes merged
    :rtype: List[nodl.types.Node]
    """
    node_lists = {path: parse_nodl(path) for path in paths}
    combined: Dict[str, '_NodeWithOrigin'] = {}
    for path, node_list in node_lists.items():
        for node in node_list:
            current_node = _NodeWithOrigin([path], node)
            if node.name not in combined:
                combined[node.name] = current_node
            else:
                try:
                    combined[node.name] += current_node
                except nodl.errors.NodeMergeConflictError as e:
                    raise FailedMergeError(error=e)
    return combined.values()


def show_nodl_parsed(*, paths: List[Path]):
    """
    Pretty print a dict-like representation of all nodes to console.

    :param paths: Names of nodl file to show
    :type paths: List[Path]

    :raises FailedMergeError: if nodes with the same name are present and cannot merge.
    """
    nodes = _merge_nodl_files(paths=paths)
    for node in nodes:
        pprint.pprint(node._as_dict)


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


class _NodeWithOrigin(nodl.types.Node):
    """Helper class to track the file(s) that a given node came from."""

    def __init__(self, paths: List[Path], node: 'nodl.types.Node') -> None:
        super().__init__(
            name=node.name,
            actions=node.actions.values(),
            parameters=node.parameters.values(),
            services=node.services.values(),
            topics=node.topics.values(),
        )
        self.paths = paths

    def __iadd__(self, other: '_NodeWithOrigin') -> '_NodeWithOrigin':
        self.paths += other.paths
        self = super().__iadd__(other)
        return self
