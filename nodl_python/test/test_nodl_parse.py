from pathlib import Path
import xml.etree.ElementTree as ETree

import pytest

import nodl


@pytest.fixture()
def valid_nodl() -> ETree.ElementTree:
    return ETree.parse(str(Path('test') / 'nodl.xml'))


def test_parse_nodl_file_valid(mocker):
    mocker.patch('nodl.nodl_parse.parse_nodl')

    # Test if accepts a valid xml file
    nodl.nodl_parse.parse_nodl_file('test/nodl.xml')


def test_parse_nodl_valid(mocker, valid_nodl):
    nodl.nodl_parse.parse_nodl(valid_nodl.getroot())


def test_parse_nodl_invalid(mocker):
    mocker.patch('nodl.nodl_parse.InterfaceParser_v1')
    not_interface = ETree.Element("notinterface")
    interface_no_version = ETree.Element("interface")
    interface_future_version = ETree.Element("interface",
                                             {'version': str(nodl.nodl_parse.NODL_MAX_SUPPORTED_VERSION + 1)})  # noqa: E501

    with pytest.raises(nodl.nodl_parse.InvalidNoDLException) as excinfo:
        nodl.nodl_parse.parse_nodl(not_interface)
    assert "Invalid root element" in str(excinfo.value)

    with pytest.raises(nodl.nodl_parse.InvalidNoDLException) as excinfo:
        nodl.nodl_parse.parse_nodl(interface_no_version)
    assert "Missing version attribute in 'interface'" in str(excinfo.value)

    with pytest.raises(nodl.nodl_parse.UnsupportedInterfaceException) as excinfo:
        nodl.nodl_parse.parse_nodl(interface_future_version)
