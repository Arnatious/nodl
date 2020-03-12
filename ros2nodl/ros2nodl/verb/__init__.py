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

from ros2cli.plugin_system import PLUGIN_SYSTEM_VERSION, satisfies_version


class VerbExtension:
    """"""

    NAME = None
    EXTENSION_POINT_VERSION = '0.1'

    def __init__(self):
        super().__init__()
        satisfies_version(PLUGIN_SYSTEM_VERSION, '^0.1')

    def add_arguments(self, parser, cli_name):
        pass

    def main(self, *, args):
        raise NotImplementedError()
