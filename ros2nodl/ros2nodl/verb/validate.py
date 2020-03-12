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

import sys
from typing import TYPE_CHECKING

from ros2nodl.api import (
    get_share_nodl_files_from_package,
    NoDLFileNameCompleter,
    NoNoDLFilesError,
    validate_nodl_file,
)
from ros2nodl.verb import VerbExtension
from ros2pkg.api import package_name_completer, PackageNotFoundError

if TYPE_CHECKING:
    import argparse


class ValidateVerb(VerbExtension):
    """Show NoDL data."""

    def add_arguments(self, parser: 'argparse.ArgumentParser', *_):
        # Ignoring type because of https://github.com/python/typeshed/issues/1878
        # TODO: remove type ignore after Foxy release
        parser.add_argument(  # type: ignore
            'package_name', help='Name of the package to validate.'
        ).completer = package_name_completer

        command_group = parser.add_mutually_exclusive_group(required=True)
        command_group.add_argument(
            '-a',
            '--all',
            '--all-files',
            default=False,
            action='store_true',
            help='Validate all .nodl.xml files in the package together.',
        )
        command_group.add_argument(  # type: ignore
            '-f', '--file', nargs='+', default=[], help='Specific .nodl.xml file(s) to validate.'
        ).completer = NoDLFileNameCompleter()

    def main(self, *, args: 'argparse.Namespace') -> int:
        try:
            package = args.package_name
            paths = get_share_nodl_files_from_package(package_name=package)
        except (PackageNotFoundError, NoNoDLFilesError) as e:
            print(e, file=sys.stderr)
            return 1

        if args.file:
            short_paths = [path.name for path in paths]
            for filename in args.file:
                if filename not in short_paths:
                    print(
                        f'{filename} not found in {package}.\n Options are {short_paths}',
                        file=sys.stderr,
                    )
                    return 1
            paths = [path for path in paths if path.name in args.file]

        for path in paths:
            print(f'Validating {path.name}...')
            if not validate_nodl_file(path=path):
                return 1
            print(f' Success')
        print(f'All files validated')
        return 0
