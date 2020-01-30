# Copyright 2020 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU Limited General Public License version 3, as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranties of MERCHANTABILITY, SATISFACTORY QUALITY,
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Limited General Public License for more details.
#
# You should have received a copy of the GNU Limited General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.

from pathlib import Path
from typing import List, Optional
import warnings

from lxml import etree

from nodl.nodl_types import Action, Node, Parameter, Service, Topic


NODL_MAX_SUPPORTED_VERSION: int = 1


def str_to_bool(boolean_string: str) -> bool:
    """Simple helper function for converting xml bool entries to bools."""
    return boolean_string.lower in ["true", "1"]


class InvalidNoDLException(Exception):
    def __init__(self, message: str, element: Optional[etree._Element] = None):
        if element:
            super().__init__(f"{element.base}:{element.sourceline}: " + message)
        else:
            super().__init__(message)


class UnsupportedInterfaceException(InvalidNoDLException):
    def __init__(self, element: etree._Element):
        super().__init__(
            f"{element.sourceline}: Unsupported interface version: {element.attrib['version']}"
            f"> {NODL_MAX_SUPPORTED_VERSION}"
        )


class NoNodeInterfaceWarning(UserWarning):
    pass


def parse_nodl_file(path: Path):
    """"""
    full_path = path.resolve()

    nodl_tree: etree._ElementTree = etree.parse(str(path))

    interface = nodl_tree.getroot()
    if nodl_tree.getroot().tag != "interface":
        interface = nodl_tree.find("interface")
        if not interface:
            raise InvalidNoDLException(f"No interface tag in {nodl_tree.docinfo.URL}")

    try:
        version = nodl_tree.attrib["version"]
    except KeyError:
        raise InvalidNoDLException(
            f"Missing version attribute in 'interface'.", interface
        )

    if version == "1":
        return InterfaceParser_v1(nodl_tree)
    else:
        raise UnsupportedInterfaceException(version)


class InterfaceParser_v1:
    """"""

    def __init__(self, interface: etree._Element):

        if type(interface) is not etree._Element:
            raise TypeError(f"Invalid type passed to interface constructor: {type(interface)}")
        self._interface = interface

    def parse_action(self, element: etree._Element) -> Action:
        """"""
        # ETree.Element contains a `get()` feature that can be used to avoid
        # a potential dict creation from accessing `element.attrib`. We don't use
        # this because we want a KeyError if the required fields aren't there.
        attribs = element.attrib
        name = attribs["name"]
        action_type = attribs["type"]

        server = str_to_bool(attribs.get("server", False))
        client = str_to_bool(attribs.get("client", False))
        if not (server or client):
            warnings.warn(
                f"{element.base}:{element.sourceline}: {name} is neither server or client",
                NoNodeInterfaceWarning
            )

        return Action(name=name, action_type=action_type, server=server, client=client)

    def parse_parameter(self, element: etree._Element) -> Parameter:
        """"""
        return Parameter(name=element.attrib["name"], parameter_type=element.attrib["type"])

    def parse_service(self, element: etree._Element) -> Service:
        """"""
        attribs = element.attrib
        name = attribs["name"]
        service_type = attribs["type"]

        server = str_to_bool(attribs.get("server", False))
        client = str_to_bool(attribs.get("client", False))

        if not (server or client):
            warnings.warn(
                f"{element.base}:{element.sourceline}: {name} is neither server or client",
                NoNodeInterfaceWarning
            )

        return Service(name=name, service_type=service_type, server=server, client=client)

    def parse_topic(self, element: etree._Element) -> Topic:
        """"""
        attribs = element.attrib
        try:
            name = attribs["name"]
            message_type = attribs["type"]
        except KeyError as e:
            raise InvalidNoDLException(
                f"Topic is missing required attribute {e.args[0]}", element
            ) from e

        publisher = str_to_bool(attribs.get("publisher", False))
        subscriber = str_to_bool(attribs.get("subscriber", False))
        return Topic(
            name=name, message_type=message_type, publisher=publisher, subscriber=subscriber
        )

    def parse_nodes(self) -> List[Node]:
        """"""

        node_elements = [child for child in self._interface if child.tag == "node"]
        return [self.parse_node(node) for node in node_elements]

    def parse_node(self, node):
        try:
            name = node.attrib["name"]
        except KeyError as e:
            raise InvalidNoDLException(f"Node is missing required attribute {e.args[0]}") from e

        actions = []
        parameters = []
        services = []
        topics = []

        for child in node:
            if child.tag == "action":
                actions.append(self.parse_action(child))
            if child.tag == "parameter":
                parameters.append(self.parse_parameter(child))
            if child.tag == "service":
                services.append(self.parse_service(child))
            if child.tag == "topic":
                topics.append(self.parse_topic(child))

        return Node(
            name=name, actions=actions, parameters=parameters, services=services, topics=topics
        )
