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

from ros2cli.command import add_subparsers_on_demand, CommandExtension

if TYPE_CHECKING:
    import argparse


class NoDLCommand(CommandExtension):
    """Access node interface descriptions exported from packages."""

    def add_arguments(
        self, parser: 'argparse.ArgumentParser', cli_name: str, *, argv: Optional[List] = None
    ):
        self._subparser = parser
        add_subparsers_on_demand(
            parser=parser,
            cli_name=cli_name,
            dest='_verb',
            group_name='ros2nodl.verb',
            required=False,
            argv=argv,
        )

    def main(self, *, parser, args):
        if not hasattr(args, '_verb'):
            self._subparser.print_help()
            return 0
        extension: CommandExtension = args._verb

        return extension.main(args=args)
