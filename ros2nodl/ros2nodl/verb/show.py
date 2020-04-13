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
    FailedMergeError,
    get_nodl_files_from_package_share,
    NoDLFileNameCompleter,
    NoNoDLFilesError,
    show_nodl_parsed,
    show_nodl_raw,
)
from ros2nodl.verb import VerbExtension
from ros2pkg.api import package_name_completer, PackageNotFoundError

if TYPE_CHECKING:
    import argparse


class ShowVerb(VerbExtension):
    """Show NoDL data."""

    def add_arguments(self, parser: 'argparse.ArgumentParser', *_):
        parser.add_argument(  # type: ignore
            'package_name', help='Name of the package to show.'
        ).completer = package_name_completer

        command_group = parser.add_mutually_exclusive_group(required=True)
        command_group.add_argument(
            '-a',
            '--all',
            '--all-files',
            default=False,
            action='store_true',
            help='Combine all .nodl.xml files and display the combined output.',
        )
        command_group.add_argument(  # type: ignore
            '-f', '--file', nargs='+', help='Specific .nodl.xml file(s) to display.'
        ).completer = NoDLFileNameCompleter()

        parser.add_argument(
            '--raw', help='Print raw file contents, without parsing.', action='store_true'
        )

    def main(self, *, args: 'argparse.Namespace') -> int:
        try:
            package = args.package_name
            paths = get_nodl_files_from_package_share(package_name=package)
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

            if args.raw:
                show_nodl_raw(paths=paths)
            else:
                try:
                    show_nodl_parsed(paths=paths)
                except FailedMergeError as e:
                    print(e, sys.stderr)
                    return 1
        return 0
