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
from typing import TYPE_CHECKING

from argcomplete.completers import FilesCompleter
from ros2nodl.api import (
    validate_nodl_file,
)
from ros2nodl.verb import VerbExtension

if TYPE_CHECKING:
    import argparse


class ValidateVerb(VerbExtension):
    """Validate NoDL XML documents."""

    def add_arguments(self, parser: 'argparse.ArgumentParser', *_):
        # Ignoring type because of https://github.com/python/typeshed/issues/1878
        # TODO: remove type ignore after Focal/Foxy release

        command_group = parser.add_mutually_exclusive_group(required=True)
        command_group.add_argument(
            '-a',
            '--all',
            '--all-files',
            default=False,
            action='store_true',
            help='Validate all .nodl.xml files in the current directory.',
        )
        command_group.add_argument(  # type: ignore
            'file', nargs='*', default=[], help='Specific .nodl.xml file(s) to validate.'
        ).completer = FilesCompleter(allowednames=['nodl.xml'], directories=False)

    def main(self, *, args: 'argparse.Namespace') -> int:
        paths = [Path(filename) for filename in args.file]
        if not paths:
            paths = list(Path.cwd().glob('*.nodl.xml'))

        for path in paths:
            if not path.is_file():
                print(f'Could not access {path.name}')
                return 1

            print(f'Validating {path.name}...')
            if not validate_nodl_file(path=path):
                return 1
            print(f' Success')
        else:
            print(f'All files validated')

        return 0
