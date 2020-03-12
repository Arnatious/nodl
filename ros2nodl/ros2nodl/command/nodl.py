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

from typing import List, Optional, TYPE_CHECKING

from ros2cli.command import add_subparsers, CommandExtension
from ros2cli.verb import get_verb_extensions

if TYPE_CHECKING:
    import argparse


class NoDLCommand(CommandExtension):
    """Access node interface descriptions exported from packages."""

    def add_arguments(
        self, parser: 'argparse.ArgumentParser', cli_name: str, *, argv: Optional[List] = None
    ):
        self._subparser = parser
        verb_extensions = get_verb_extensions('ros2nodl.verb')
        add_subparsers(
            parser, cli_name, '_verb', verb_extensions, required=False
        )

    def main(self, *, parser, args):
        if not hasattr(args, '_verb'):
            self._subparser.print_help()
            return 0
        extension: CommandExtension = args._verb

        return extension.main(args=args)
