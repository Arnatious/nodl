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
from typing import List, Optional, TYPE_CHECKING

import ament_index_python
import nodl
import nodl.errors

if TYPE_CHECKING:  # pragma: no cover
    import nodl.types
    import argparse


def show_nodl_raw(*, paths: List[Path]):
    """Print filename and contents to console.

    :param paths: Names of nodl files to show
    :type paths: List[Path]
    """
    for path in paths:
        print(f'{path.name}:\n' + ('-' * 80) + '\n')
        print(path.read_text())


def show_nodl_parsed(*, paths: List[Path]):
    """Pretty print a dict-like representation of all nodes to console.

    :param paths: Names of nodl file to show
    :type paths: List[Path]

    :raises DuplicateNodeError: if nodes with the same name are present.
    """
    nodes = nodl.parse_multiple(paths=paths)
    for node in nodes:
        pprint.pprint(node._as_dict)


class NoDLFileNameCompleter:
    """Callable returning a list of nodl file names within a package's share directory."""

    def __init__(self, *, package_name_key: Optional[str] = None) -> None:
        self.package_name_key = 'package_name' if package_name_key is None else package_name_key

    def __call__(self, *, parsed_args: 'argparse.Namespace', **kwargs) -> List[str]:
        """Return a list of file names for nodl files found within the package.

        :param prefix: [description]
        :type prefix: str
        :param parsed_args: [description]
        :type parsed_args: [type]
        """
        package_name = getattr(parsed_args, self.package_name_key)
        try:
            return [
                path.name
                for path in nodl.get_nodl_files_from_package_share(package_name=package_name)
            ]
        except ament_index_python.PackageNotFoundError:
            return ['package not found']
