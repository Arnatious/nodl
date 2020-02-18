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

from typing import List, TYPE_CHECKING

from lxml import etree
from nodl._parsing import _v1 as parse_v1
from nodl._parsing._schemas import get_schema
from nodl.exception import InvalidNoDLError, UnsupportedInterfaceError
from nodl.types import Node

if TYPE_CHECKING:
    import pathlib


NODL_MAX_SUPPORTED_VERSION = 1


_SCHEMA = get_schema('interface.xsd')


def _parse_interface(interface: etree._Element) -> List[Node]:
    """Parse out all nodes from an interface element."""
    if interface.get('version') == '1':
        return parse_v1._validate_and_parse(interface)
    else:
        raise UnsupportedInterfaceError(interface.get('version'), NODL_MAX_SUPPORTED_VERSION)


def _parse_element_tree(element_tree: etree._ElementTree) -> List[Node]:
    """Extract an interface element from an ElementTree if present."""
    try:
        _SCHEMA.assertValid(element_tree)
    except etree.DocumentInvalid as e:
        if e.error_log[0].type == etree.ErrorTypes.SCHEMAV_CVC_ELT_1:
            raise InvalidNoDLError(
                f'Failed to parse root interface element: {e}', e
            ) from e
        raise InvalidNoDLError('Document Invalid', e)
    return _parse_interface(element_tree.getroot())


def _parse_nodl_file(path: 'pathlib.Path') -> List[Node]:
    """Parse the nodes out of a given NoDL file."""
    full_path = path.resolve()
    element_tree = etree.parse(str(full_path))

    return _parse_element_tree(element_tree)