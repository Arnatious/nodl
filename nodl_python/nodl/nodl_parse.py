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
    return boolean_string.lower() in ["true", "1"]


class InvalidNoDLException(Exception):
    def __init__(self, message: str, element: Optional[etree._Element] = None) -> None:
        if element is not None:
            super().__init__(f"{element.base}:{element.sourceline}: " + message)
        else:
            super().__init__(message)


class UnsupportedInterfaceException(InvalidNoDLException):
    def __init__(self, element: etree._Element) -> None:
        super().__init__(
            f"{element.base}:{element.sourceline}: Unsupported interface version: "
            f"{element.attrib['version']} > {NODL_MAX_SUPPORTED_VERSION}"
        )


class NoNodeInterfaceWarning(UserWarning):
    pass


def parse_element_tree(element_tree: etree._ElementTree) -> etree._Element:
    interface = element_tree.getroot()
    if interface.tag != "interface":
        interface = interface.find("interface")
        if interface is None:
            raise InvalidNoDLException(f"No interface tag in {element_tree.docinfo.URL}")
    return interface


def parse_nodl_file(path: Path):
    """"""
    full_path = path.resolve()
    element_tree = etree.parse(str(full_path))
    interface = parse_element_tree(element_tree)

    try:
        version = interface.attrib["version"]
    except KeyError:
        raise InvalidNoDLException(f"Missing version attribute in 'interface'.", interface)

    if version == "1":
        return Interface_v1(interface)
    else:
        raise UnsupportedInterfaceException(interface)


class Interface_v1:
    """"""

    def __init__(self, interface: etree._Element) -> None:
        self._interface = interface

    @classmethod
    def parse_action(cls, element: etree._Element) -> Action:
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
                NoNodeInterfaceWarning,
            )

        return Action(name=name, action_type=action_type, server=server, client=client)

    @classmethod
    def parse_parameter(cls, element: etree._Element) -> Parameter:
        """"""
        return Parameter(name=element.attrib["name"], parameter_type=element.attrib["type"])

    @classmethod
    def parse_service(cls, element: etree._Element) -> Service:
        """"""
        attribs = element.attrib
        name = attribs["name"]
        service_type = attribs["type"]

        server = str_to_bool(attribs.get("server", False))
        client = str_to_bool(attribs.get("client", False))

        if not (server or client):
            warnings.warn(
                f"{element.base}:{element.sourceline}: {name} is neither server or client",
                NoNodeInterfaceWarning,
            )

        return Service(name=name, service_type=service_type, server=server, client=client)

    @classmethod
    def parse_topic(cls, element: etree._Element) -> Topic:
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

        if not (publisher or subscriber):
            warnings.warn(
                f"{element.base}:{element.sourceline}: {name} is neither publisher or subscriber",
                NoNodeInterfaceWarning,
            )

        return Topic(
            name=name, message_type=message_type, publisher=publisher, subscriber=subscriber
        )

    @classmethod
    def parse_nodes(cls) -> List[Node]:
        """"""

        node_elements = [child for child in cls._interface if child.tag == "node"]
        return [cls.parse_node(node) for node in node_elements]

    @classmethod
    def parse_node(cls, node):
        try:
            name = node.attrib["name"]
        except KeyError as e:
            raise InvalidNoDLException(f"Node is missing required attribute {e.args[0]}") from e

        actions = []
        parameters = []
        services = []
        topics = []

        for child in node:
            try:
                if child.tag == "action":
                    actions.append(cls.parse_action(child))
                if child.tag == "parameter":
                    parameters.append(cls.parse_parameter(child))
                if child.tag == "service":
                    services.append(cls.parse_service(child))
                if child.tag == "topic":
                    topics.append(cls.parse_topic(child))
            except KeyError as excinfo:
                raise InvalidNoDLException(
                    f"{child.tag} is missing required attribute {excinfo.args[0]}", child
                )

        return Node(
            name=name, actions=actions, parameters=parameters, services=services, topics=topics
        )
