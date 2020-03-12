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
import sys
from typing import List, Optional, TYPE_CHECKING

from ament_index_python.packages import get_package_share_directory, PackageNotFoundError
from nodl import parse as parse_nodl
import nodl.errors


if TYPE_CHECKING:
    import argparse


class NoNoDLFilesError(Exception):
    """Exception raised when a package has no NoDL files in the ament index."""

    def __init__(self, package_name):
        super().__init__(f'{package_name} has no NoDL files in its ament index.')


def get_share_nodl_files_from_package(*, package_name: str) -> List[Path]:
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


def show_nodl(*, path: Path, raw: bool = False):
    """
    Print filename and either contents or NoDL data to console.

    :param path: Name of nodl file to show
    :type path: Path
    :param raw: Whether to print file as-is or parse, defaults to False
    :type raw: bool, optional
    """
    if raw:
        show_nodl_file(path=path)
    else:
        show_nodl_parsed(path=path)


def show_nodl_file(*, path: Path):
    """
    Print filename and contents to console.

    :param path: Name of nodl file to show
    :type path: Path
    """
    print(f'{path.name}:\n' + ('-' * 80) + '\n')
    print(path.read_text())


def show_nodl_parsed(*, path: Path) -> bool:
    """
    Print filename and contents to console.

    :param path: Name of nodl file to show
    :type path: Path
    """
    try:
        nodes = parse_nodl(path)
    except nodl.errors.InvalidNoDLDocumentError as e:
        print(f'Parsing of {path.name} failed', file=sys.stderr)
        print(e, file=sys.stderr)
        return False
    print(f'{path.name}:\n' + ('-' * 80) + '\n')
    for node in nodes:
        pprint.pprint(node._as_dict)
    return True


def validate_nodl_file(*, path: Path) -> bool:
    """"""
    try:
        parse_nodl(path)
    except nodl.errors.InvalidNoDLDocumentError as e:
        print(f'Validation of {str(path)} failed', file=sys.stderr)
        print(e, file=sys.stderr)
        return False
    return True


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
                path.name for path in get_share_nodl_files_from_package(package_name=package_name)
            ]
        except PackageNotFoundError:
            return ['package not found']
